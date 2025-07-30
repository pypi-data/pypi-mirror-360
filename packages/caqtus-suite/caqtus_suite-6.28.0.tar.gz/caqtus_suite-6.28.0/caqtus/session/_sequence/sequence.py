from __future__ import annotations

import datetime
from collections.abc import Iterable, Mapping
from functools import cached_property
from typing import TYPE_CHECKING, Optional, Self, Literal, assert_never

import attrs
import polars
from typing_extensions import deprecated

from caqtus.device import DeviceName, DeviceConfiguration
from caqtus.types.data import DataLabel, DataType
from caqtus.types.iteration import IterationConfiguration, Unknown
from caqtus.types.parameter import ParameterNamespace, ParameterSchema
from caqtus.types.timelane import TimeLanes
from caqtus.types.variable_name import DottedVariableName
from caqtus.utils.result._result import is_failure
from .shot import Shot
from .._exception_summary import TracebackSummary
from .._exceptions import PathIsNotSequenceError, PathNotFoundError
from .._path import PureSequencePath
from .._state import State
from ...utils.result import is_failure_type

if TYPE_CHECKING:
    from .._experiment_session import ExperimentSession
    from caqtus.analysis.loading import DataImporter


def _convert_to_path(path: PureSequencePath | str) -> PureSequencePath:
    if isinstance(path, str):
        return PureSequencePath(path)
    return path


@attrs.frozen(eq=False, order=False)
class Sequence:
    """Represent a sequence in the experiment session.

    Sequence objects can be obtained by calling :meth:`ExperimentSession.get_sequence`.
    The returned sequence object is bound to the session and is only valid in the
    context where the session is active.

    Args:
        path: The path of the sequence.
        session: The session to which the sequence belongs.
            The sequence is bound to the session and is only valid in the context where
            the session is active.
    """

    path: PureSequencePath = attrs.field(converter=_convert_to_path)
    session: ExperimentSession

    def __attrs_post_init__(self):
        is_sequence_result = self.session.sequences.is_sequence(self.path)
        if is_failure_type(is_sequence_result, PathNotFoundError):
            import difflib

            contained_sequences_result = self.session.sequences.get_contained_sequences(
                PureSequencePath.root()
            )
            assert not is_failure_type(contained_sequences_result, PathNotFoundError)
            sequences = contained_sequences_result.result()
            paths = [str(sequence) for sequence in sequences]
            similar_paths = difflib.get_close_matches(str(self.path), paths)
            e = PathNotFoundError(self.path)
            if similar_paths:
                e.add_note(f'Perhaps you meant: "{similar_paths[0]}"')
            raise e
        else:
            if not is_sequence_result.result():
                raise PathIsNotSequenceError(self.path)

    @classmethod
    def create(
        cls,
        path: PureSequencePath,
        iteration_configuration: IterationConfiguration,
        time_lanes: TimeLanes,
        session: ExperimentSession,
    ) -> Self:
        """Create a new sequence in the session.

        Args:
            path: The path at which to create the sequence.
            iteration_configuration: How the sequence parameters should be iterated
                over.
            time_lanes: How the shots should be run.
            session: The session in which the sequence should be created.
                The session must be active.
        """

        session.sequences.create(path, iteration_configuration, time_lanes).unwrap()
        return cls(path, session)

    def __str__(self) -> str:
        return str(self.path)

    def __len__(self) -> int:
        """Return the number of shots that have been run for this sequence."""

        return len(self.session.sequences.get_shots(self.path).unwrap())

    def get_state(self) -> State:
        """Return the state of the sequence."""

        return self.session.sequences.get_state(self.path).unwrap()

    def get_global_parameters(self) -> ParameterNamespace:
        """Return a copy of the parameter tables set for this sequence.

        Raises:
            RuntimeError: If the sequence is in DRAFT state, since the global parameters
                are only set once the sequence has entered the PREPARING state.
        """

        return self.session.sequences.get_global_parameters(self.path).unwrap()

    def get_iteration_configuration(self) -> IterationConfiguration:
        """Return the iteration configuration of the sequence."""

        return self.session.sequences.get_iteration_configuration(self.path)

    def get_time_lanes(self) -> TimeLanes:
        """Return the time lanes that define how a shot is run for this sequence."""

        result = self.session.sequences.get_time_lanes(self.path)
        if is_failure(result):
            raise result.exception()
        return result

    def set_time_lanes(self, time_lanes: TimeLanes) -> None:
        """Set the time lanes that define how a shot is run for this sequence."""

        result = self.session.sequences.set_time_lanes(self.path, time_lanes)
        if is_failure(result):
            raise result.exception()

    def get_shots(self) -> Iterable[Shot]:
        """Return the shots that belong to this sequence.

        The shots are returned sorted by index.
        """

        pure_shots = self.session.sequences.get_shots(self.path).unwrap()
        sorted_shots = sorted(pure_shots, key=lambda x: x.index)
        return (Shot(self, shot.index, self.session) for shot in sorted_shots)

    def get_start_time(self) -> Optional[datetime.datetime]:
        """Return the time the sequence was started.

        If the sequence has not been started, return None.
        """

        return self.session.sequences.get_stats(self.path).unwrap().start_time

    def get_end_time(self) -> Optional[datetime.datetime]:
        """Return the time the sequence was ended.

        If the sequence has not been ended, return None.
        """

        return self.session.sequences.get_stats(self.path).unwrap().stop_time

    def get_expected_number_of_shots(self) -> int | Unknown:
        """Return the expected number of shots for the sequence.

        If the sequence has not been started, return None.
        """

        return (
            self.session.sequences.get_stats(self.path).unwrap().expected_number_shots
        )

    def duplicate(self, target_path: PureSequencePath | str) -> Sequence:
        """Duplicate the sequence to a new path.

        The sequence created will be in the draft state and will have the same iteration
        configuration and time lanes as the original sequence.
        """

        if isinstance(target_path, str):
            target_path = PureSequencePath(target_path)

        iteration_configuration = self.get_iteration_configuration()
        time_lanes = self.get_time_lanes()
        self.create(target_path, iteration_configuration, time_lanes, self.session)
        return Sequence(target_path, self.session)

    def get_device_configurations(self) -> dict[DeviceName, DeviceConfiguration]:
        """Return the device configurations used when the sequence was launched."""

        device_configurations = self.session.sequences.get_device_configurations(
            self.path
        ).unwrap()

        return dict(device_configurations)

    def get_local_parameters(self) -> set[DottedVariableName]:
        """Return the name of the parameters specifically set for this sequence."""

        return self._sequence_parameters

    def get_parameter_names(
        self, which: Literal["all", "sequence"]
    ) -> set[DottedVariableName]:
        """Return the name of the parameters used to run this sequence.

        Args:
            which: Which parameters to return.

                * all: Return both sequence specific and global parameters.
                * local: Return only the parameters specifically set for this sequence.

        Returns:
            The names of the parameters used to run this sequence.
        """

        if which == "all":
            return self._all_parameters
        elif which == "sequence":
            return self._sequence_parameters
        else:
            assert_never(which)

    @cached_property
    def _all_parameters(self) -> set[DottedVariableName]:
        """The name of the parameters used to run this sequence."""

        global_parameters = self.get_global_parameters()
        return global_parameters.names() | self._sequence_parameters

    @cached_property
    def _sequence_parameters(self) -> set[DottedVariableName]:
        """The name of the parameters specifically set for this sequence."""

        iterations = self.get_iteration_configuration()
        return iterations.get_parameter_names()

    def get_traceback_summary(self) -> Optional[TracebackSummary]:
        """Return the traceback summary of the sequence.

        Return:
            The summary of the exception that crashed the sequence if one could be
            retrieved, otherwise None.

        Raises:
            SequenceNotCrashedError: If the sequence is not in the CRASHED state.
        """

        return self.session.sequences.get_exception(self.path).unwrap()

    def get_parameter_schema(self) -> ParameterSchema:
        """Return the types of the parameters used to run this sequence.

        Examples:
            Get the units of a parameter:

            .. code-block:: python

                schema = sequence.get_parameter_schema()
                schema["mot.detuning"].units
                # Unit("MHz")
        """

        return self.session.sequences.get_parameter_schema(self.path).unwrap()

    def get_data_schema(self) -> Mapping[DataLabel, DataType]:
        return self.session.sequences.get_data_schema(self.path).unwrap()

    def scan(self) -> polars.LazyFrame:
        r"""Lazily read the data of the shots that have been run for this sequence.

        Calling this function does not yet load any data.
        Instead, you should apply operations on the returned lazyframe and then call
        :meth:`polars.LazyFrame.collect` to load the data.
        This will only fetch the data necessary to perform the requested operations.

        Returns:
            A lazy dataframe that can be used to fetch the data of the shots that
            have been run for this sequence.
            Each row in the dataframe corresponds to a shot.

            The first columns contain the following metadata:

                * sequence: The name of the sequence the shot belongs to.
                * shot_index: The index of the shot in the sequence.
                * shot_start_time: The time the shot started.
                * shot_end_time: The time the shot ended.

            The dataframe then contains columns for all the shot parameters and
            generated data.

        Example:

        >>> data = sequence.scan().head().collect()
        ┌──────────┬────────────┬─────────────────────┬────────────────────┬──────────┬────────────────────┐
        │ sequence ┆ shot_index ┆ shot_start_time     ┆ shot_end_time      ┆ exposure ┆ Camera\picture 1   │
        │ ---      ┆ ---        ┆ ---                 ┆ ---                ┆ ---      ┆ ---                │
        │ cat      ┆ u64        ┆ datetime[ms, UTC]   ┆ datetime[ms, UTC]  ┆ f64      ┆ array[u32, (100,   │
        │          ┆            ┆                     ┆                    ┆          ┆ 100)]              │
        ╞══════════╪════════════╪═════════════════════╪════════════════════╪══════════╪════════════════════╡
        │ \test    ┆ 0          ┆ 2025-03-15          ┆ 2025-03-15         ┆ 0.0      ┆ [[0, 0, … 0], [0,  │
        │          ┆            ┆ 14:03:30.476 UTC    ┆ 14:03:30.476 UTC   ┆          ┆ 0, … 0], … […      │
        │ \test    ┆ 1          ┆ 2025-03-15          ┆ 2025-03-15         ┆ 1.0      ┆ [[1, 1, … 1], [1,  │
        │          ┆            ┆ 14:03:30.478 UTC    ┆ 14:03:30.478 UTC   ┆          ┆ 1, … 1], … […      │
        │ \test    ┆ 2          ┆ 2025-03-15          ┆ 2025-03-15         ┆ 2.0      ┆ [[2, 2, … 2], [2,  │
        │          ┆            ┆ 14:03:30.486 UTC    ┆ 14:03:30.486 UTC   ┆          ┆ 2, … 2], … […      │
        │ \test    ┆ 3          ┆ 2025-03-15          ┆ 2025-03-15         ┆ 3.0      ┆ [[3, 3, … 3], [3,  │
        │          ┆            ┆ 14:03:30.490 UTC    ┆ 14:03:30.490 UTC   ┆          ┆ 3, … 3], … […      │
        │ \test    ┆ 4          ┆ 2025-03-15          ┆ 2025-03-15         ┆ 4.0      ┆ [[4, 4, … 4], [4,  │
        │          ┆            ┆ 14:03:30.492 UTC    ┆ 14:03:30.492 UTC   ┆          ┆ 4, … 4], … […      │
        └──────────┴────────────┴─────────────────────┴────────────────────┴──────────┴────────────────────┘
        """  # noqa: E501

        return self.session.sequences.scan(self.path).unwrap()

    @deprecated("use sequence.scan() instead")
    def load_shots_data(
        self,
        importer: "DataImporter",
        tags: Optional[polars.type_aliases.FrameInitTypes] = None,
    ) -> Iterable[polars.DataFrame]:
        """Load the data of the shots that have been run for this sequence.

        Args:
            importer: A function that takes a shot and returns the data of the shot.
                It will be called for each shot in the sequence.
            tags: An optional object that can be converted to a 1-row DataFrame.
                The dataframe will be joined with the data of each shot.
                This allows to add extra information to the dataframes returned for this
                sequence.

        Yields:
            Dataframes containing the data of the shots in the sequence ordered by shot
            index.

        .. deprecated:: 6.24.0

            Use :meth:`scan` instead as it is faster and easier to use.
        """

        if tags is not None:
            tags_dataframe = polars.DataFrame(tags)
            if len(tags_dataframe) != 1:
                raise ValueError("tags should be a single row DataFrame")
        else:
            tags_dataframe = None

        data_labels = set[DataLabel]()

        for shot in self.get_shots():
            # Here we use a trick to speed up data loading.
            # We keep track of the data labels that have been loaded so far and
            # reload them before passing them to the importer.
            # This ensure that data are queried in group, with is more efficient.
            shot.get_data_by_labels(data_labels)
            data = importer(shot)
            data_labels = set(shot._data_cache.keys())

            if tags_dataframe is not None:
                yield data.join(tags_dataframe, how="cross")
            else:
                yield data

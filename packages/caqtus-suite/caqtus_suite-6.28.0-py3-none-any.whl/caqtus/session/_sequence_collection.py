from __future__ import annotations

import abc
import datetime
from collections.abc import Mapping, Set, Iterable
from typing import Protocol, Optional, Literal, TYPE_CHECKING

import attrs
import polars

from caqtus.device import DeviceName, DeviceConfiguration
from caqtus.types.data import DataLabel, Data, DataType
from caqtus.types.iteration import IterationConfiguration, Unknown
from caqtus.types.parameter import Parameter, ParameterNamespace, ParameterSchema
from caqtus.types.timelane import TimeLanes
from caqtus.types.variable_name import DottedVariableName
from caqtus.utils.result import Success, Failure, is_failure_type, is_failure
from ._data_id import DataId
from ._exception_summary import TracebackSummary
from ._exceptions import (
    PathIsSequenceError,
    PathIsNotSequenceError,
    InvalidStateTransitionError,
    SequenceNotEditableError,
    SequenceNotCrashedError,
    PathNotFoundError,
    PathHasChildrenError,
)
from ._exceptions import SequenceNotRunningError, SequenceNotLaunchedError
from ._path import PureSequencePath
from ._shot_id import ShotId
from ._state import State
from ..shot_compilation import SequenceContext

if TYPE_CHECKING:
    from ._experiment_session import ExperimentSession


class SequenceCollection(Protocol):
    """A collection of sequences inside a session.

    This abstract class defines the interface to read and write sequences in a session.
    Objects of this class provide methods for full access to read/write operations on
    sequences and their shots.
    However, they are not meant to be convenient to use directly in user code.
    Instead, consider using the higher-level API provided by the
    :class:`caqtus.session.Sequence` and :class:`caqtus.session.Shot` classes to access
    data from sequences and shots.
    """

    @property
    def parent_session(self) -> "ExperimentSession":
        """The session that this collection belongs to."""

        ...

    @abc.abstractmethod
    def is_sequence(
        self, path: PureSequencePath
    ) -> Success[bool] | Failure[PathNotFoundError]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_contained_sequences(
        self, path: PureSequencePath
    ) -> Success[Set[PureSequencePath]] | Failure[PathNotFoundError]:
        """Return the descendants of this path that are sequences.

        The current path is included in the result if it is a sequence.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def get_global_parameters(
        self, path: PureSequencePath
    ) -> (
        Success[ParameterNamespace]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[SequenceNotLaunchedError]
    ):
        """Get the global parameters that were used by this sequence.

        Raises:
            RuntimeError: If the sequence is in draft mode, since the global parameters
            are only set once the sequence has entered the PREPARING state.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def get_iteration_configuration(
        self, sequence: PureSequencePath
    ) -> IterationConfiguration:
        """Return a copy of the iteration configuration for this sequence."""

        raise NotImplementedError

    @abc.abstractmethod
    def set_iteration_configuration(
        self,
        sequence: PureSequencePath,
        iteration_configuration: IterationConfiguration,
    ) -> (
        None
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[SequenceNotEditableError]
    ):
        """Set the iteration configuration for this sequence."""

        raise NotImplementedError

    @abc.abstractmethod
    def get_time_lanes(
        self, sequence_path: PureSequencePath
    ) -> TimeLanes | Failure[PathNotFoundError] | Failure[PathIsNotSequenceError]:
        """Return a copy of the time lanes for this sequence."""

        raise NotImplementedError

    @abc.abstractmethod
    def set_time_lanes(
        self, sequence_path: PureSequencePath, time_lanes: TimeLanes
    ) -> (
        None
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[SequenceNotEditableError]
    ):
        """Set the time lanes that define how a shot is run for this sequence."""

        raise NotImplementedError

    @abc.abstractmethod
    def get_device_configurations(
        self, path: PureSequencePath
    ) -> (
        Success[Mapping[DeviceName, DeviceConfiguration]]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[SequenceNotLaunchedError]
    ):
        """Get the device configurations that are used by this sequence."""

        raise NotImplementedError

    @abc.abstractmethod
    def create(
        self,
        path: PureSequencePath,
        iteration_configuration: IterationConfiguration,
        time_lanes: TimeLanes,
    ) -> Success[None] | Failure[PathIsSequenceError] | Failure[PathHasChildrenError]:
        """Create a new sequence at the given path.

        Returns:
            PathIsSequenceError: If the path already exists and is a sequence.
            PathHasChildrenError: If the path already exists and has children.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def get_state(
        self, path: PureSequencePath
    ) -> Success[State] | Failure[PathNotFoundError] | Failure[PathIsNotSequenceError]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_exception(
        self, path: PureSequencePath
    ) -> (
        Success[Optional[TracebackSummary]]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[SequenceNotCrashedError]
    ):
        """Return the exceptions that occurred while running the sequence.

        Returns:
            A result wrapping the exceptions that occurred while running the sequence.

            Even if the sequence is in the CRASHED state, there may not be any
            exceptions captured. In this case, the result will be None.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def set_preparing(
        self,
        path: PureSequencePath,
        device_configurations: Mapping[DeviceName, DeviceConfiguration],
        global_parameters: ParameterNamespace,
    ) -> (
        Success[None]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[InvalidStateTransitionError]
    ):
        """Set a sequence to the PREPARING state.

        Args:
            path: The path to the sequence to prepare.
            device_configurations: The configurations of the devices that were used to
                run this sequence.
            global_parameters: The parameters used to run the sequence.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def set_running(
        self, path: PureSequencePath, start_time: datetime.datetime | Literal["now"]
    ) -> (
        Success[None]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[InvalidStateTransitionError]
    ):
        """Set a sequence to the RUNNING state.

        Args:
            path: The path to the sequence.
            start_time: The time at which the sequence started running.
                Must be a timezone-aware datetime object.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def set_finished(
        self, path: PureSequencePath, stop_time: datetime.datetime | Literal["now"]
    ) -> (
        Success[None]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[InvalidStateTransitionError]
    ):
        """Set a sequence to the FINISHED state.

        Args:
            path: The path to the sequence.
            stop_time: The time at which the sequence stopped running.
                Must be a timezone-aware datetime object.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def set_interrupted(
        self, path: PureSequencePath, stop_time: datetime.datetime | Literal["now"]
    ) -> (
        Success[None]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[InvalidStateTransitionError]
    ):
        """Set a sequence to the INTERRUPTED state.

        Args:
            path: The path to the sequence.
            stop_time: The time at which the sequence was interrupted.
                Must be a timezone-aware datetime object.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def set_crashed(
        self,
        path: PureSequencePath,
        tb_summary: TracebackSummary,
        stop_time: datetime.datetime | Literal["now"],
    ) -> (
        Success[None]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[InvalidStateTransitionError]
    ):
        """Set the sequence to the CRASHED state.

        Args:
            path: The path of the sequence to set to the CRASHED state.
            tb_summary: A summary of the error that caused the sequence to crash.
                This summary will be saved with the sequence.
            stop_time: The time at which the sequence crashed.
                Must be a timezone-aware datetime object.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def reset_to_draft(
        self, path: PureSequencePath
    ) -> (
        Success[None]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[InvalidStateTransitionError]
    ):
        """Reset the sequence to the DRAFT state.

        Warning:
            This method removes all data associated to the sequence.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def get_stats(
        self, path: PureSequencePath
    ) -> (
        Success[SequenceStats]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def create_shot(
        self,
        shot_id: ShotId,
        shot_parameters: Mapping[DottedVariableName, Parameter],
        shot_data: Mapping[DataLabel, Data],
        shot_start_time: datetime.datetime,
        shot_end_time: datetime.datetime,
    ) -> (
        Success[None]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[SequenceNotRunningError]
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def get_shots(
        self, path: PureSequencePath
    ) -> (
        Success[list[ShotId]]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
    ):
        """Return the shots that belong to this sequence."""

        raise NotImplementedError

    @abc.abstractmethod
    def get_shot_parameters(
        self, path: PureSequencePath, shot_index: int
    ) -> Mapping[DottedVariableName, Parameter]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_all_shot_data(
        self, path: PureSequencePath, shot_index: int
    ) -> Mapping[DataLabel, Data]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_shot_data_by_label(self, data: DataId) -> Data:
        """Return the data with the given label for the shot at the given index.

        Raises:
            PathNotFoundError: If the path does not exist in the session.
            PathIsNotSequenceError: If the path is not a sequence.
            ShotNotFoundError: If the shot does not exist in the sequence.
            DataNotFoundError: If the data with the given label does not exist in the
            shot.
        """

        raise NotImplementedError

    def get_shot_data_by_labels(
        self, path: PureSequencePath, shot_index: int, data_labels: Set[DataLabel]
    ) -> Mapping[DataLabel, Data]:
        """Return the data with the given labels for the shot at the given index.

        This method is equivalent to calling :meth:`get_shot_data_by_label` for each
        label in the set, but can be faster.

        Raises:
            PathNotFoundError: If the path does not exist in the session.
            PathIsNotSequenceError: If the path is not a sequence.
            ShotNotFoundError: If the shot does not exist in the sequence.
            DataNotFoundError: If one of the data labels does not exist in the shot.
        """

        # Naive implementation that calls get_shot_data_by_label for each label.
        shot_id = ShotId(path, shot_index)
        return {
            label: self.get_shot_data_by_label(DataId(shot_id, label))
            for label in data_labels
        }

    @abc.abstractmethod
    def get_shot_start_time(
        self, path: PureSequencePath, shot_index: int
    ) -> datetime.datetime:
        raise NotImplementedError

    @abc.abstractmethod
    def get_shot_end_time(
        self, path: PureSequencePath, shot_index: int
    ) -> datetime.datetime:
        raise NotImplementedError

    @abc.abstractmethod
    def get_sequences_in_state(self, state: State) -> Iterable[PureSequencePath]:
        """Return all sequences in the given state."""

        raise NotImplementedError

    def get_parameter_schema(
        self, path: PureSequencePath
    ) -> (
        Success[ParameterSchema]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
    ):
        """Return the parameter schema for this sequence."""

        globals_result = self.get_global_parameters(path)
        if is_failure_type(globals_result, SequenceNotLaunchedError):
            sequence_globals = self.parent_session.get_global_parameters()
        elif is_failure(globals_result):
            return globals_result
        else:
            sequence_globals = globals_result.value

        iterations = self.get_iteration_configuration(path)

        initial_values = sequence_globals.evaluate()

        schema = iterations.get_parameter_schema(initial_values)
        return Success(schema)

    def get_data_schema(
        self, path: PureSequencePath
    ) -> (
        Success[Mapping[DataLabel, DataType]]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[SequenceNotLaunchedError]
    ):
        device_configurations_result = self.get_device_configurations(path)
        if is_failure(device_configurations_result):
            return device_configurations_result
        device_configurations = device_configurations_result.content()
        parameter_schema_result = self.get_parameter_schema(path)
        if is_failure(parameter_schema_result):
            return parameter_schema_result
        parameter_schema = parameter_schema_result.content()
        time_lanes = self.get_time_lanes(path)
        if is_failure(time_lanes):
            return time_lanes
        sequence_context = SequenceContext(
            device_configurations, parameter_schema, time_lanes
        )
        schema = {}
        for device_name, device_configuration in device_configurations.items():
            device_schema = {
                f"{device_name}\\{label}": data_type
                for label, data_type in device_configuration.get_data_schema(
                    device_name, sequence_context
                )
                .unwrap()
                .items()
            }
            schema.update(device_schema)
        return Success(schema)

    @abc.abstractmethod
    def scan(
        self, path: PureSequencePath
    ) -> (
        Success[polars.LazyFrame]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[SequenceNotLaunchedError]
    ):
        raise NotImplementedError


@attrs.frozen
class SequenceStats:
    state: State
    start_time: Optional[datetime.datetime]
    stop_time: Optional[datetime.datetime]
    number_completed_shots: int
    expected_number_shots: int | Unknown

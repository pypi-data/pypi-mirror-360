from __future__ import annotations

import datetime
from collections.abc import Mapping, Iterable, Set
from typing import (
    TYPE_CHECKING,
    Optional,
    assert_never,
    assert_type,
    Literal,
)

import attrs
import cattrs
import numpy as np
import polars
import sqlalchemy.orm
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from caqtus.device import DeviceName, DeviceConfiguration
from caqtus.types.data import Data
from caqtus.types.data import is_data, DataLabel
from caqtus.types.iteration import (
    IterationConfiguration,
    Unknown,
)
from caqtus.types.parameter import Parameter, ParameterNamespace
from caqtus.types.timelane import TimeLanes
from caqtus.types.units import Quantity
from caqtus.types.variable_name import DottedVariableName
from caqtus.utils import serialization
from caqtus.utils.result import (
    Success,
    Failure,
    is_failure_type,
    is_success,
    is_failure,
    unwrap,
)
from ._lazy_load import scan, structure_shot_sql_data
from ._logger import logger
from ._path_hierarchy import _query_path_model
from ._path_table import SQLSequencePath
from ._sequence_table import (
    SQLSequence,
    SQLIterationConfiguration,
    SQLTimelanes,
    SQLDeviceConfiguration,
    SQLSequenceParameters,
    SQLExceptionTraceback,
)
from ._serializer import SerializerProtocol
from ._shot_tables import SQLShot, SQLShotParameter, SQLShotArray, SQLStructuredShotData
from .._data_id import DataId
from .._exception_summary import TracebackSummary
from .._exceptions import (
    SequenceNotRunningError,
    SequenceNotLaunchedError,
    PathIsSequenceError,
    PathIsNotSequenceError,
    DataNotFoundError,
    InvalidStateTransitionError,
    SequenceNotEditableError,
    SequenceNotCrashedError,
    ShotNotFoundError,
    PathNotFoundError,
    PathIsRootError,
    PathHasChildrenError,
)
from .._path import PureSequencePath
from .._sequence_collection import SequenceCollection, SequenceStats
from .._shot_id import ShotId
from .._state import State

if TYPE_CHECKING:
    from ._experiment_session import SQLExperimentSession


@attrs.frozen
class SQLSequenceCollection(SequenceCollection):
    _parent_session: "SQLExperimentSession"
    serializer: SerializerProtocol

    @property
    def parent_session(self) -> "SQLExperimentSession":
        return self._parent_session

    def is_sequence(
        self, path: PureSequencePath
    ) -> Success[bool] | Failure[PathNotFoundError]:
        return _is_sequence(self._get_sql_session(), path)

    def get_contained_sequences(
        self, path: PureSequencePath
    ) -> Success[set[PureSequencePath]] | Failure[PathNotFoundError]:
        path_result = _query_path_model(self._get_sql_session(), path)
        if is_failure_type(path_result, PathNotFoundError):
            return path_result

        result = set()
        if is_failure_type(path_result, PathIsRootError):
            ancestor_id = None
        else:
            ancestor_id = path_result.value.id_

            if path_result.value.sequence is not None:
                result.add(path)

        sequences_query = self.descendant_sequences(ancestor_id)

        query = self._get_sql_session().execute(sequences_query).scalars().all()
        return Success({PureSequencePath(row.path.path) for row in query} | result)

    def descendant_sequences(
        self, ancestor_id: Optional[int]
    ) -> sqlalchemy.sql.Select[tuple[SQLSequence]]:
        """Returns a query for the descendant sequences of the given ancestor.

        The ancestor is not included in the result.
        """

        descendants = self.parent_session.paths.descendants_query(ancestor_id)
        sequences_query = select(SQLSequence).join(
            descendants,
            SQLSequence.path_id == descendants.id_,
        )
        return sequences_query

    def get_contained_running_sequences(
        self, path: PureSequencePath
    ) -> Success[set[PureSequencePath]] | Failure[PathNotFoundError]:
        path_model_result = _query_path_model(self._get_sql_session(), path)

        running_sequences = set()
        if isinstance(path_model_result, Failure):
            if is_failure_type(path_model_result, PathNotFoundError):
                return path_model_result
            assert_type(path_model_result, Failure[PathIsRootError])
            parent_id = None
        else:
            path_model = path_model_result.value

            if path_model.sequence is not None:
                if path_model.sequence.state in {State.PREPARING, State.RUNNING}:
                    running_sequences.add(path)
            parent_id = path_model.id_

        sequences_query = self.descendant_sequences(parent_id)
        running_sequences_query = sequences_query.where(
            SQLSequence.state.in_({State.PREPARING, State.RUNNING})
        )

        result = (
            self._get_sql_session().execute(running_sequences_query).scalars().all()
        )
        running_sequences.update(PureSequencePath(row.path.path) for row in result)
        return Success(running_sequences)

    def _set_global_parameters(
        self, path: PureSequencePath, parameters: ParameterNamespace
    ) -> None:
        sequence = unwrap(self._query_sequence_model(path))
        if sequence.state != State.PREPARING:
            raise SequenceNotEditableError(path)

        if not isinstance(parameters, ParameterNamespace):
            raise TypeError(
                f"Invalid parameters type {type(parameters)}, "
                f"expected ParameterNamespace"
            )

        parameters_content = serialization.converters["json"].unstructure(
            parameters, ParameterNamespace
        )

        sequence.parameters.content = parameters_content

    def get_global_parameters(
        self, path: PureSequencePath
    ) -> (
        Success[ParameterNamespace]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[SequenceNotLaunchedError]
    ):
        return _get_sequence_global_parameters(self._get_sql_session(), path)

    def get_iteration_configuration(
        self, sequence: PureSequencePath
    ) -> IterationConfiguration:
        return _get_iteration_configuration(
            self._get_sql_session(), sequence, self.serializer
        )

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
        return _set_iteration_configuration(
            self._get_sql_session(), sequence, iteration_configuration, self.serializer
        )

    def create(
        self,
        path: PureSequencePath,
        iteration_configuration: IterationConfiguration,
        time_lanes: TimeLanes,
    ) -> Success[None] | Failure[PathIsSequenceError] | Failure[PathHasChildrenError]:
        children_result = self.parent_session.paths.get_children(path)
        if is_success(children_result):
            if children_result.value:
                return Failure(PathHasChildrenError(path))
        else:
            if is_failure_type(children_result, PathIsSequenceError):
                return children_result
            elif is_failure_type(children_result, PathNotFoundError):
                creation_result = self.parent_session.paths.create_path(path)
                if is_failure(creation_result):
                    if is_failure_type(creation_result, PathIsSequenceError):
                        return creation_result
                    assert_never(creation_result)
            else:
                assert_never(children_result)

        iteration_content = self.serializer.dump_sequence_iteration(
            iteration_configuration
        )

        new_sequence = SQLSequence(
            path=unwrap(self._query_path_model(path)),
            parameters=SQLSequenceParameters(content=None),
            iteration=SQLIterationConfiguration(content=iteration_content),
            time_lanes=SQLTimelanes(content=self.serialize_time_lanes(time_lanes)),
            state=State.DRAFT,
            device_configurations=[],
            start_time=None,
            stop_time=None,
            expected_number_of_shots=_convert_from_unknown(
                iteration_configuration.expected_number_shots()
            ),
        )
        self._get_sql_session().add(new_sequence)
        return Success(None)

    def serialize_time_lanes(self, time_lanes: TimeLanes) -> serialization.JSON:
        return self.serializer.unstructure_time_lanes(time_lanes)

    def get_time_lanes(
        self, sequence_path: PureSequencePath
    ) -> TimeLanes | Failure[PathNotFoundError] | Failure[PathIsNotSequenceError]:
        return _get_time_lanes(self._get_sql_session(), sequence_path, self.serializer)

    def set_time_lanes(
        self, sequence_path: PureSequencePath, time_lanes: TimeLanes
    ) -> (
        None
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[SequenceNotEditableError]
    ):
        return _set_time_lanes(
            self._get_sql_session(), sequence_path, time_lanes, self.serializer
        )

    def get_state(
        self, path: PureSequencePath
    ) -> Success[State] | Failure[PathNotFoundError] | Failure[PathIsNotSequenceError]:
        result = self._query_sequence_model(path)
        return result.map(lambda sequence: sequence.state)

    def get_exception(
        self, path: PureSequencePath
    ) -> (
        Success[Optional[TracebackSummary]]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[SequenceNotCrashedError]
    ):
        return _get_exceptions(self._get_sql_session(), path)

    def _set_exception(
        self, path: PureSequencePath, exception: TracebackSummary
    ) -> (
        Success[None]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[SequenceNotCrashedError]
    ):
        return _set_exception(self._get_sql_session(), path, exception)

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
        sequence_result = _query_sequence_model(self._get_sql_session(), path)
        if is_failure(sequence_result):
            return sequence_result
        sequence = sequence_result.value
        if not State.is_transition_allowed(sequence.state, State.PREPARING):
            return Failure(
                InvalidStateTransitionError(
                    f"Sequence at {path} can't transition from {sequence.state} to "
                    f"{State.PREPARING}"
                )
            )
        sequence.state = State.PREPARING
        self._set_device_configurations(path, device_configurations)
        self._set_global_parameters(path, global_parameters)
        return Success(None)

    def set_running(
        self, path: PureSequencePath, start_time: datetime.datetime | Literal["now"]
    ) -> (
        Success[None]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[InvalidStateTransitionError]
    ):
        sequence_result = _query_sequence_model(self._get_sql_session(), path)
        if is_failure(sequence_result):
            return sequence_result
        sequence = sequence_result.content()
        if not State.is_transition_allowed(sequence.state, State.RUNNING):
            return Failure(
                InvalidStateTransitionError(
                    f"Sequence at {path} can't transition from {sequence.state} to "
                    f"{State.RUNNING}"
                )
            )
        sequence.state = State.RUNNING
        if start_time == "now":
            start_time = datetime.datetime.now(tz=datetime.timezone.utc)
        if not is_tz_aware(start_time):
            raise ValueError("Start time must be timezone aware")
        sequence.start_time = start_time.astimezone(datetime.timezone.utc).replace(
            tzinfo=None
        )
        return Success(None)

    def set_finished(
        self, path: PureSequencePath, stop_time: datetime.datetime | Literal["now"]
    ) -> (
        Success[None]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[InvalidStateTransitionError]
    ):
        sequence_result = _query_sequence_model(self._get_sql_session(), path)
        if is_failure(sequence_result):
            return sequence_result
        sequence = sequence_result.value
        if not State.is_transition_allowed(sequence.state, State.FINISHED):
            return Failure(
                InvalidStateTransitionError(
                    f"Sequence at {path} can't transition from {sequence.state} to "
                    f"{State.FINISHED}"
                )
            )
        sequence.state = State.FINISHED
        if stop_time == "now":
            stop_time = datetime.datetime.now(tz=datetime.timezone.utc)
        if not is_tz_aware(stop_time):
            raise ValueError("Stop time must be timezone aware")
        sequence.stop_time = stop_time.astimezone(datetime.timezone.utc).replace(
            tzinfo=None
        )
        return Success(None)

    def set_interrupted(
        self, path: PureSequencePath, stop_time: datetime.datetime | Literal["now"]
    ) -> (
        Success[None]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[InvalidStateTransitionError]
    ):
        sequence_result = _query_sequence_model(self._get_sql_session(), path)
        if is_failure(sequence_result):
            return sequence_result
        sequence = sequence_result.value
        if not State.is_transition_allowed(sequence.state, State.INTERRUPTED):
            return Failure(
                InvalidStateTransitionError(
                    f"Sequence at {path} can't transition from {sequence.state} to "
                    f"{State.INTERRUPTED}"
                )
            )
        sequence.state = State.INTERRUPTED
        if stop_time == "now":
            stop_time = datetime.datetime.now(tz=datetime.timezone.utc)
        if not is_tz_aware(stop_time):
            raise ValueError("Stop time must be timezone aware")
        sequence.stop_time = stop_time.astimezone(datetime.timezone.utc).replace(
            tzinfo=None
        )
        return Success(None)

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
        sequence_result = _query_sequence_model(self._get_sql_session(), path)
        if is_failure(sequence_result):
            return sequence_result
        sequence = sequence_result.value
        if not State.is_transition_allowed(sequence.state, State.CRASHED):
            return Failure(
                InvalidStateTransitionError(
                    f"Sequence at {path} can't transition from {sequence.state} to "
                    f"{State.CRASHED}"
                )
            )
        sequence.state = State.CRASHED
        if stop_time == "now":
            stop_time = datetime.datetime.now(tz=datetime.timezone.utc)
        if not is_tz_aware(stop_time):
            raise ValueError("Stop time must be timezone aware")
        sequence.stop_time = stop_time.astimezone(datetime.timezone.utc).replace(
            tzinfo=None
        )
        set_exception_result = self._set_exception(path, tb_summary)
        assert not is_failure_type(set_exception_result, PathNotFoundError)
        assert not is_failure_type(set_exception_result, PathIsNotSequenceError)
        assert not is_failure_type(set_exception_result, SequenceNotCrashedError)
        assert_type(set_exception_result, Success[None])
        return Success(None)

    def reset_to_draft(
        self, path: PureSequencePath
    ) -> (
        Success[None]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[InvalidStateTransitionError]
    ):
        return _reset_to_draft(self._get_sql_session(), path)

    def _set_device_configurations(
        self,
        path: PureSequencePath,
        device_configurations: Mapping[DeviceName, DeviceConfiguration],
    ) -> None:
        sequence = unwrap(self._query_sequence_model(path))
        if sequence.state != State.PREPARING:
            raise SequenceNotEditableError(path)
        sql_device_configs = []
        for name, device_configuration in device_configurations.items():
            type_name, content = self.serializer.dump_device_configuration(
                device_configuration
            )
            sql_device_configs.append(
                SQLDeviceConfiguration(
                    name=name, device_type=type_name, content=content
                )
            )
        sequence.device_configurations = sql_device_configs

    def get_device_configurations(
        self, path: PureSequencePath
    ) -> (
        Success[dict[DeviceName, DeviceConfiguration]]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[SequenceNotLaunchedError]
    ):
        return _get_device_configurations(
            self._get_sql_session(), path, self.serializer
        )

    def get_stats(
        self, path: PureSequencePath
    ) -> (
        Success[SequenceStats]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
    ):
        return _get_stats(self._get_sql_session(), path)

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
        return _create_shot(
            self._get_sql_session(),
            shot_id,
            shot_parameters,
            shot_data,
            shot_start_time,
            shot_end_time,
        )

    def get_shots(
        self, path: PureSequencePath
    ) -> (
        Success[list[ShotId]]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
    ):
        return _get_shots(self._get_sql_session(), path)

    def get_shot_parameters(
        self, path: PureSequencePath, shot_index: int
    ) -> Mapping[DottedVariableName, Parameter]:
        return _get_shot_parameters(self._get_sql_session(), path, shot_index)

    def get_all_shot_data(
        self, path: PureSequencePath, shot_index: int
    ) -> dict[DataLabel, Data]:
        return _get_all_shot_data(self._get_sql_session(), path, shot_index)

    def get_shot_data_by_label(self, data: DataId) -> Data:
        return _get_shot_data_by_label(self._get_sql_session(), data)

    def get_shot_data_by_labels(
        self, path: PureSequencePath, shot_index: int, data_labels: Set[DataLabel]
    ) -> Mapping[DataLabel, Data]:
        return _get_shot_data_by_labels(
            self._get_sql_session(), path, shot_index, data_labels
        )

    def get_shot_start_time(
        self, path: PureSequencePath, shot_index: int
    ) -> datetime.datetime:
        return _get_shot_start_time(self._get_sql_session(), path, shot_index)

    def get_shot_end_time(
        self, path: PureSequencePath, shot_index: int
    ) -> datetime.datetime:
        return _get_shot_end_time(self._get_sql_session(), path, shot_index)

    def get_sequences_in_state(self, state: State) -> Iterable[PureSequencePath]:
        stmt = (
            select(SQLSequencePath).join(SQLSequence).where(SQLSequence.state == state)
        )
        result = self._get_sql_session().execute(stmt).scalars().all()
        return (PureSequencePath(row.path) for row in result)

    def scan(
        self, path: PureSequencePath
    ) -> (
        Success[polars.LazyFrame]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[SequenceNotLaunchedError]
    ):
        session = self._get_sql_session()
        sequence_model_result = _query_sequence_model(session, path)
        if is_failure(sequence_model_result):
            return sequence_model_result
        sequence_model = sequence_model_result.content()
        parameter_schema_result = self.get_parameter_schema(path)
        assert not is_failure_type(
            parameter_schema_result, (PathNotFoundError, PathIsNotSequenceError)
        )
        parameter_schema = parameter_schema_result.content()
        if sequence_model.state == State.DRAFT:
            return Failure(SequenceNotLaunchedError(path))
        data_schema_result = self.get_data_schema(path)
        assert not is_failure_type(
            data_schema_result,
            (PathNotFoundError, PathIsNotSequenceError, SequenceNotLaunchedError),
        )
        data_schema = data_schema_result.content()
        return Success(
            scan(
                session,
                sequence_model,
                {str(k): v for k, v in parameter_schema.items()},
                {str(k): v for k, v in data_schema.items()},
            )
        )

    def _query_path_model(
        self, path: PureSequencePath
    ) -> (
        Success[SQLSequencePath] | Failure[PathNotFoundError] | Failure[PathIsRootError]
    ):
        return _query_path_model(self._get_sql_session(), path)

    def _query_sequence_model(
        self, path: PureSequencePath
    ) -> (
        Success[SQLSequence]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
    ):
        return _query_sequence_model(self._get_sql_session(), path)

    def _query_shot_model(
        self, path: PureSequencePath, shot_index: int
    ) -> (
        Success[SQLShot]
        | Failure[PathNotFoundError]
        | Failure[PathIsNotSequenceError]
        | Failure[ShotNotFoundError]
    ):
        return _query_shot_model(self._get_sql_session(), path, shot_index)

    def _get_sql_session(self) -> sqlalchemy.orm.Session:
        # noinspection PyProtectedMember
        return self.parent_session._get_sql_session()


def _convert_from_unknown(value: int | Unknown) -> Optional[int]:
    if isinstance(value, Unknown):
        return None
    elif isinstance(value, int):
        return value
    else:
        assert_never(value)


def _convert_to_unknown(value: Optional[int]) -> int | Unknown:
    if value is None:
        return Unknown()
    elif isinstance(value, int):
        return value
    else:
        assert_never(value)


def _is_sequence(
    session: Session, path: PureSequencePath
) -> Success[bool] | Failure[PathNotFoundError]:
    path_model_result = _query_path_model(session, path)
    if isinstance(path_model_result, Failure):
        if is_failure_type(path_model_result, PathNotFoundError):
            return path_model_result
        else:
            assert_type(path_model_result, Failure[PathIsRootError])
            return Success(False)
    else:
        path_model = path_model_result.value
        return Success(bool(path_model.sequence))


def _get_exceptions(
    session: Session, path: PureSequencePath
) -> (
    Success[Optional[TracebackSummary]]
    | Failure[PathNotFoundError]
    | Failure[PathIsNotSequenceError]
    | Failure[SequenceNotCrashedError]
):
    sequence_model_query = _query_sequence_model(session, path)
    match sequence_model_query:
        case Success(sequence_model):
            assert isinstance(sequence_model, SQLSequence)
            if sequence_model.state != State.CRASHED:
                return Failure(SequenceNotCrashedError(path))
            exception_model = sequence_model.exception_traceback
            if exception_model is None:
                return Success(None)
            else:
                traceback_summary = cattrs.structure(
                    exception_model.content, TracebackSummary
                )
                return Success(traceback_summary)
        case Failure() as failure:
            return failure


def _set_exception(
    session: Session, path: PureSequencePath, exception: TracebackSummary
) -> (
    Success[None]
    | Failure[PathNotFoundError]
    | Failure[PathIsNotSequenceError]
    | Failure[SequenceNotCrashedError]
):
    sequence_model_query = _query_sequence_model(session, path)
    match sequence_model_query:
        case Success(sequence_model):
            assert isinstance(sequence_model, SQLSequence)
            if sequence_model.state != State.CRASHED:
                return Failure(SequenceNotCrashedError(path))
            if sequence_model.exception_traceback is not None:
                raise RuntimeError("Exception already set")
            content = cattrs.unstructure(exception, TracebackSummary)
            sequence_model.exception_traceback = SQLExceptionTraceback(content=content)
            return Success(None)
        case Failure() as failure:
            return failure


def _get_stats(
    session: Session, path: PureSequencePath
) -> (
    Success[SequenceStats]
    | Failure[PathNotFoundError]
    | Failure[PathIsNotSequenceError]
):
    result = _query_sequence_model(session, path)

    def extract_stats(sequence: SQLSequence) -> SequenceStats:
        number_shot_query = select(func.count()).select_from(
            select(SQLShot).where(SQLShot.sequence == sequence).subquery()
        )
        number_shot_run = session.execute(number_shot_query).scalar_one()
        return SequenceStats(
            state=sequence.state,
            start_time=(
                sequence.start_time.replace(tzinfo=datetime.timezone.utc)
                if sequence.start_time is not None
                else None
            ),
            stop_time=(
                sequence.stop_time.replace(tzinfo=datetime.timezone.utc)
                if sequence.stop_time is not None
                else None
            ),
            number_completed_shots=number_shot_run,
            expected_number_shots=_convert_to_unknown(
                sequence.expected_number_of_shots
            ),
        )

    return result.map(extract_stats)


def _get_sequence_global_parameters(
    session: Session, path: PureSequencePath
) -> (
    Success[ParameterNamespace]
    | Failure[PathNotFoundError]
    | Failure[PathIsNotSequenceError]
    | Failure[SequenceNotLaunchedError]
):
    sequence_result = _query_sequence_model(session, path)
    if is_failure(sequence_result):
        return sequence_result
    sequence = sequence_result.value

    if sequence.state == State.DRAFT:
        return Failure(
            SequenceNotLaunchedError(f"Sequence at {path} is in DRAFT state")
        )

    parameters_content = sequence.parameters.content

    return Success(
        serialization.converters["json"].structure(
            parameters_content, ParameterNamespace
        )
    )


def _get_iteration_configuration(
    session: Session, sequence: PureSequencePath, serializer: SerializerProtocol
) -> IterationConfiguration:
    sequence_model = unwrap(_query_sequence_model(session, sequence))
    return serializer.construct_sequence_iteration(
        sequence_model.iteration.content,
    )


def _set_iteration_configuration(
    session: Session,
    sequence: PureSequencePath,
    iteration_configuration: IterationConfiguration,
    serializer: SerializerProtocol,
) -> (
    None
    | Failure[PathNotFoundError]
    | Failure[PathIsNotSequenceError]
    | Failure[SequenceNotEditableError]
):
    sequence_model_result = _query_sequence_model(session, sequence)
    if is_failure(sequence_model_result):
        return sequence_model_result
    sequence_model = sequence_model_result.content()
    if not sequence_model.state.is_editable():
        raise SequenceNotEditableError(sequence)
    iteration_content = serializer.dump_sequence_iteration(iteration_configuration)
    sequence_model.iteration.content = iteration_content
    expected_number_shots = iteration_configuration.expected_number_shots()
    sequence_model.expected_number_of_shots = _convert_from_unknown(
        expected_number_shots
    )


def _get_time_lanes(
    session: Session, sequence_path: PureSequencePath, serializer: SerializerProtocol
) -> TimeLanes | Failure[PathNotFoundError] | Failure[PathIsNotSequenceError]:
    sequence_model_result = _query_sequence_model(session, sequence_path)
    if is_failure(sequence_model_result):
        return sequence_model_result
    sequence_model = sequence_model_result.content()
    return serializer.structure_time_lanes(sequence_model.time_lanes.content)


def _set_time_lanes(
    session: Session,
    sequence_path: PureSequencePath,
    time_lanes: TimeLanes,
    serializer: SerializerProtocol,
) -> (
    None
    | Failure[PathNotFoundError]
    | Failure[PathIsNotSequenceError]
    | Failure[SequenceNotEditableError]
):
    sequence_model_result = _query_sequence_model(session, sequence_path)
    if is_failure(sequence_model_result):
        return sequence_model_result
    sequence_model = sequence_model_result.content()
    if not sequence_model.state.is_editable():
        return Failure(SequenceNotEditableError(sequence_path))
    sequence_model.time_lanes.content = serializer.unstructure_time_lanes(time_lanes)


def _get_shots(
    session: Session, path: PureSequencePath
) -> (
    Success[list[ShotId]] | Failure[PathNotFoundError] | Failure[PathIsNotSequenceError]
):
    sql_sequence = _query_sequence_model(session, path)

    def extract_shots(sql_sequence: SQLSequence) -> list[ShotId]:
        return [ShotId(path, shot.index) for shot in sql_sequence.shots]

    return sql_sequence.map(extract_shots)


def _get_shot_parameters(
    session: Session, path: PureSequencePath, shot_index: int
) -> Mapping[DottedVariableName, Parameter]:
    stmt = (
        select(SQLShotParameter.content)
        .join(SQLShot)
        .where(SQLShot.index == shot_index)
        .join(SQLSequence)
        .join(SQLSequencePath)
        .where(SQLSequencePath.path == str(path))
    )

    result = session.execute(stmt).scalar_one_or_none()
    if result is not None:
        return serialization.converters["json"].structure(
            result, dict[DottedVariableName, bool | int | float | Quantity]
        )
    # This will raise the proper error if the shot was not found.
    unwrap(_query_shot_model(session, path, shot_index))
    raise AssertionError("Unreachable code")


def _create_shot(
    session: Session,
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
    sequence_result = _query_sequence_model(session, shot_id.sequence_path)
    if is_failure(sequence_result):
        return sequence_result
    sequence = sequence_result.value
    if sequence.state != State.RUNNING:
        return Failure(SequenceNotRunningError(shot_id.sequence_path))
    if shot_id.index < 0:
        raise ValueError("Shot index must be non-negative")
    if sequence.expected_number_of_shots is not None:
        if shot_id.index >= sequence.expected_number_of_shots:
            raise ValueError(
                f"Shot index must be less than the expected number of shots "
                f"({sequence.expected_number_of_shots})"
            )

    parameters = serialize_shot_parameters(shot_parameters)

    array_data, structured_data = serialize_data(shot_data)

    shot = SQLShot(
        sequence=sequence,
        index=shot_id.index,
        parameters=SQLShotParameter(content=parameters),
        array_data=array_data,
        structured_data=structured_data,
        start_time=shot_start_time.astimezone(datetime.timezone.utc).replace(
            tzinfo=None
        ),
        end_time=shot_end_time.astimezone(datetime.timezone.utc).replace(tzinfo=None),
    )
    session.add(shot)
    return Success(None)


def _get_all_shot_data(
    session: Session, path: PureSequencePath, shot_index: int
) -> dict[DataLabel, Data]:
    shot_model = unwrap(_query_shot_model(session, path, shot_index))
    arrays = shot_model.array_data
    structured_data = shot_model.structured_data
    result = {}
    for array in arrays:
        result[array.label] = structure_shot_sql_data(array)
    for data in structured_data:
        result[data.label] = structure_shot_sql_data(data)
    return result


def _get_shot_data_by_label(
    session: Session,
    data: DataId,
) -> Data:
    return _get_shot_data_by_labels(
        session, data.shot_id.sequence_path, data.shot_id.index, {data.data_label}
    )[data.data_label]


def _get_shot_data_by_labels(
    session: Session,
    path: PureSequencePath,
    shot_index: int,
    data_labels: Set[DataLabel],
) -> dict[DataLabel, Data]:
    content = unwrap(_query_data_model(session, path, shot_index, data_labels))

    data = {}

    for label, value in content.items():
        if isinstance(value, SQLStructuredShotData):
            data[label] = value.content
        elif isinstance(value, SQLShotArray):
            data[label] = np.frombuffer(value.bytes_, dtype=value.dtype).reshape(
                value.shape
            )
        else:
            assert_never(value)
    return data


def _get_shot_start_time(
    session: Session, path: PureSequencePath, shot_index: int
) -> datetime.datetime:
    shot_model = unwrap(_query_shot_model(session, path, shot_index))
    return shot_model.get_start_time()


def _get_shot_end_time(
    session: Session, path: PureSequencePath, shot_index: int
) -> datetime.datetime:
    shot_model = unwrap(_query_shot_model(session, path, shot_index))
    return shot_model.get_end_time()


def _query_data_model(
    session: Session,
    path: PureSequencePath,
    shot_index: int,
    data_labels: Set[DataLabel],
) -> (
    Success[dict[DataLabel, SQLShotArray | SQLStructuredShotData]]
    | Failure[PathNotFoundError]
    | Failure[PathIsNotSequenceError]
    | Failure[ShotNotFoundError]
    | Failure[DataNotFoundError]
):
    data = {}
    data_labels = set(data_labels)
    stmt = (
        select(SQLStructuredShotData)
        .where(SQLStructuredShotData.label.in_(data_labels))
        .join(SQLShot)
        .where(SQLShot.index == shot_index)
        .join(SQLSequence)
        .join(SQLSequencePath)
        .where(SQLSequencePath.path == str(path))
    )
    results = session.execute(stmt).all()
    for (result,) in results:
        data[result.label] = result
        data_labels.remove(result.label)
    if not data_labels:
        return Success(data)
    stmt = (
        select(SQLShotArray)
        .where(SQLShotArray.label.in_(data_labels))
        .join(SQLShot)
        .where(SQLShot.index == shot_index)
        .join(SQLSequence)
        .join(SQLSequencePath)
        .where(SQLSequencePath.path == str(path))
    )
    results = session.execute(stmt).all()
    for (result,) in results:
        data[result.label] = result
        data_labels.remove(result.label)
    if not data_labels:
        return Success(data)
    shot_result = _query_shot_model(session, path, shot_index)
    match shot_result:
        case Success():
            return Failure(DataNotFoundError(data_labels))
        case Failure() as failure:
            return failure


def _query_sequence_model(
    session: Session, path: PureSequencePath
) -> (
    Success[SQLSequence] | Failure[PathNotFoundError] | Failure[PathIsNotSequenceError]
):
    stmt = (
        select(SQLSequence)
        .join(SQLSequencePath)
        .where(SQLSequencePath.path == str(path))
    )
    result = session.execute(stmt).scalar_one_or_none()
    if result is not None:
        return Success(result)
    else:
        # If we are not is the happy path, we need to check the reason why to be able to
        # return the correct error.
        path_result = _query_path_model(session, path)
        if isinstance(path_result, Success):
            return Failure(PathIsNotSequenceError(path))
        else:
            if is_failure_type(path_result, PathNotFoundError):
                return path_result
            else:
                assert_type(path_result, Failure[PathIsRootError])
                return Failure(PathIsNotSequenceError(path))


def _query_shot_model(
    session: Session, path: PureSequencePath, shot_index: int
) -> (
    Success[SQLShot]
    | Failure[PathNotFoundError]
    | Failure[PathIsNotSequenceError]
    | Failure[ShotNotFoundError]
):
    stmt = (
        select(SQLShot)
        .where(SQLShot.index == shot_index)
        .join(SQLSequence)
        .join(SQLSequencePath)
        .where(SQLSequencePath.path == str(path))
    )

    result = session.execute(stmt).scalar_one_or_none()
    if result is not None:
        return Success(result)
    else:
        # This function is fast for the happy path were the shot exists, but if it was
        # not found, we need to check the reason why to be able to return the correct
        # error.
        sequence_model_result = _query_sequence_model(session, path)
        match sequence_model_result:
            case Success():
                return Failure(
                    ShotNotFoundError(
                        f"Shot {shot_index} not found for sequence {path}"
                    )
                )
            case Failure() as failure:
                return failure
            case _:
                assert_never(sequence_model_result)


def _get_device_configurations(
    session: Session, path: PureSequencePath, serializer: SerializerProtocol
) -> (
    Success[dict[DeviceName, DeviceConfiguration]]
    | Failure[PathNotFoundError]
    | Failure[PathIsNotSequenceError]
    | Failure[SequenceNotLaunchedError]
):
    sequence_result = _query_sequence_model(session, path)
    if is_failure(sequence_result):
        return sequence_result
    sequence = sequence_result.content()
    if sequence.state == State.DRAFT:
        return Failure(
            SequenceNotLaunchedError(f"Sequence at {path} is in DRAFT state")
        )

    device_configurations = {}

    for device_configuration in sequence.device_configurations:
        try:
            constructed = serializer.load_device_configuration(
                device_configuration.device_type, device_configuration.content
            )
        except Exception as e:
            logger.error(
                "Could not load device configuration for %s\n%r",
                device_configuration,
                device_configuration.content,
            )
            raise DeserializationError(
                f"Failed to load device configuration for "
                f"<{device_configuration.name}> with tag "
                f"<{device_configuration.device_type}>"
            ) from e
        device_configurations[device_configuration.name] = constructed
    return Success(device_configurations)


class DeserializationError(Exception):
    pass


def _reset_to_draft(
    session: Session, path: PureSequencePath
) -> (
    Success[None]
    | Failure[PathNotFoundError]
    | Failure[PathIsNotSequenceError]
    | Failure[InvalidStateTransitionError]
):
    sequence_result = _query_sequence_model(session, path)
    if is_failure(sequence_result):
        return sequence_result
    sequence = sequence_result.value
    if not State.is_transition_allowed(sequence.state, State.DRAFT):
        return Failure(
            InvalidStateTransitionError(
                f"Sequence at {path} can't transition from {sequence.state} to "
                f"{State.DRAFT}"
            )
        )
    sequence.state = State.DRAFT
    sequence.start_time = None
    sequence.stop_time = None
    sequence.parameters.content = None
    if sequence.exception_traceback:
        session.delete(sequence.exception_traceback)
        sequence.exception_traceback = None
    delete_device_configurations = sqlalchemy.delete(SQLDeviceConfiguration).where(
        SQLDeviceConfiguration.sequence == sequence
    )
    session.execute(delete_device_configurations)

    delete_shots = sqlalchemy.delete(SQLShot).where(SQLShot.sequence == sequence)
    session.execute(delete_shots)
    return Success(None)


def serialize_data(
    data: Mapping[DataLabel, Data],
) -> tuple[list[SQLShotArray], list[SQLStructuredShotData]]:
    arrays = []
    structured_data = []
    for label, value in data.items():
        if not is_data(value):
            raise TypeError(f"Invalid data type for {label}: {type(value)}")
        if isinstance(value, np.ndarray):
            arrays.append(
                SQLShotArray(
                    label=label,
                    dtype=str(value.dtype),
                    shape=value.shape,
                    bytes_=value.tobytes(),
                )
            )
        else:
            structured_data.append(SQLStructuredShotData(label=label, content=value))
    return arrays, structured_data


def serialize_shot_parameters(
    shot_parameters: Mapping[DottedVariableName, Parameter]
) -> dict[str, serialization.JSON]:
    return {
        str(variable_name): serialization.converters["json"].unstructure(
            parameter, Parameter
        )
        for variable_name, parameter in shot_parameters.items()
    }


def is_tz_aware(dt: datetime.datetime) -> bool:
    return dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None

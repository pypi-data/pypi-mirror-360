"""Contains the copy function to transfer data between two sessions."""

from typing import assert_never, assert_type

import tqdm

from caqtus.utils.result import (
    Success,
    Failure,
    is_failure,
    is_failure_type,
    unwrap,
)
from .._exception_summary import TracebackSummary
from .._exceptions import (
    SequenceNotLaunchedError,
    PathIsSequenceError,
    PathIsNotSequenceError,
    SequenceStateError,
    InvalidStateTransitionError,
    SequenceNotCrashedError,
    PathNotFoundError,
    PathIsRootError,
    PathHasChildrenError,
)
from .._experiment_session import ExperimentSession
from .._path import PureSequencePath
from .._session_maker import ExperimentSessionMaker
from .._shot_id import ShotId
from .._state import State


def copy_path(
    path: PureSequencePath,
    source: ExperimentSessionMaker,
    destination: ExperimentSessionMaker,
) -> None:
    """Copy the path and its descendants from one session to another.

    Args:
        path: The path to copy.
        source: Used to connect to the storage when the data to be copied is located.
            The path must exist in the source session.
        destination: Used to connect to the storage where the data will be copied.
            The path must not exist in the destination session.
    """

    with source() as source_session, destination() as destination_session:
        unwrap(_copy_path(path, source_session, destination_session))


def _copy_path(
    path: PureSequencePath,
    source_session: ExperimentSession,
    destination_session: ExperimentSession,
) -> (
    Success[None]
    | Failure[PathIsSequenceError]
    | Failure[PathNotFoundError]
    | Failure[SequenceStateError]
    | Failure[PathHasChildrenError]
):
    """Copy the path and its descendants from one session to another."""

    result = copy_paths_only(path, source_session, destination_session)
    if is_failure(result):
        return result
    sequences_to_copy = result.content()
    progress_bar = tqdm.tqdm(sequences_to_copy)
    for sequence in progress_bar:
        progress_bar.set_description(f"Copying {sequence}")
        copy_sequence_result = copy_sequence(
            sequence, source_session, destination_session
        )
        if is_failure(copy_sequence_result):
            return copy_sequence_result
    return Success(None)


def copy_paths_only(
    path: PureSequencePath,
    source_session: ExperimentSession,
    destination_session: ExperimentSession,
) -> (
    Success[list[PureSequencePath]]
    | Failure[PathIsSequenceError]
    | Failure[PathNotFoundError]
):
    """Copy the path and its descendants, ignoring sequences.

    Returns a list of sequences encountered inside the path.
    """

    path_creation_result = destination_session.paths.create_path(path)
    if is_failure(path_creation_result):
        return path_creation_result
    created_paths = path_creation_result.content()
    for created_path in created_paths:
        creation_date_result = source_session.paths.get_path_creation_date(created_path)
        assert not is_failure_type(creation_date_result, PathIsRootError)
        if is_failure(creation_date_result):
            return creation_date_result
        creation_date = creation_date_result.content()
        destination_session.paths.update_creation_date(created_path, creation_date)
    children_result = source_session.paths.get_children(path)
    if is_failure_type(children_result, PathNotFoundError):
        return children_result
    elif is_failure_type(children_result, PathIsSequenceError):
        return Success([path])
    else:
        children = children_result.content()
        result = []
        for child in children:
            copy_child_result = copy_paths_only(
                child, source_session, destination_session
            )
            if is_failure(copy_child_result):
                return copy_child_result
            result.extend(copy_child_result.content())
        return Success(result)


def copy_sequence(
    path: PureSequencePath,
    source_session: ExperimentSession,
    destination_session: ExperimentSession,
) -> Success[None] | Failure[SequenceStateError] | Failure[PathHasChildrenError]:
    sequence_stats_result = source_session.sequences.get_stats(path)
    assert not is_failure_type(sequence_stats_result, PathNotFoundError)
    assert not is_failure_type(sequence_stats_result, PathIsNotSequenceError)
    stats = sequence_stats_result.value
    state = stats.state
    if state in {State.RUNNING, State.PREPARING}:
        return Failure(SequenceStateError("Can't copy running sequence"))
    iterations = source_session.sequences.get_iteration_configuration(path)
    time_lanes = source_session.sequences.get_time_lanes(path)
    assert not is_failure_type(time_lanes, (PathNotFoundError, PathIsNotSequenceError))

    creation_result = destination_session.sequences.create(path, iterations, time_lanes)
    assert not is_failure_type(creation_result, PathIsSequenceError)
    if is_failure(creation_result):
        return creation_result

    if state == State.DRAFT:
        return Success(None)
    device_configs = source_session.sequences.get_device_configurations(path)
    assert not is_failure_type(
        device_configs,
        (PathNotFoundError, PathIsNotSequenceError, SequenceNotLaunchedError),
    )
    global_parameters = unwrap(source_session.sequences.get_global_parameters(path))
    preparing_result = destination_session.sequences.set_preparing(
        path, device_configs.content(), global_parameters
    )
    assert not is_failure_type(preparing_result, PathNotFoundError)
    assert not is_failure_type(preparing_result, PathIsNotSequenceError)
    assert not is_failure_type(preparing_result, InvalidStateTransitionError)
    assert_type(preparing_result, Success[None])

    assert stats.start_time is not None
    running_result = destination_session.sequences.set_running(
        path, start_time=stats.start_time
    )
    assert not is_failure_type(running_result, PathNotFoundError)
    assert not is_failure_type(running_result, PathIsNotSequenceError)

    for shot_index in tqdm.trange(stats.number_completed_shots):
        shot_parameters = source_session.sequences.get_shot_parameters(path, shot_index)
        shot_data = source_session.sequences.get_all_shot_data(path, shot_index)
        shot_start_time = source_session.sequences.get_shot_start_time(path, shot_index)
        shot_stop_time = source_session.sequences.get_shot_end_time(path, shot_index)
        unwrap(
            destination_session.sequences.create_shot(
                ShotId(path, shot_index),
                shot_parameters,
                shot_data,
                shot_start_time,
                shot_stop_time,
            )
        )

    if state == State.FINISHED:
        assert stats.stop_time is not None
        destination_session.sequences.set_finished(path, stop_time=stats.stop_time)
    elif state == State.INTERRUPTED:
        assert stats.stop_time is not None
        destination_session.sequences.set_interrupted(path, stop_time=stats.stop_time)
    elif state == State.CRASHED:
        exception_result = source_session.sequences.get_exception(path)
        assert not is_failure_type(exception_result, PathNotFoundError)
        assert not is_failure_type(exception_result, PathIsNotSequenceError)
        assert not is_failure_type(exception_result, SequenceNotCrashedError)
        exception = exception_result.value
        if exception is None:
            exception = TracebackSummary.from_exception(RuntimeError("Unknown error"))
        assert stats.stop_time is not None
        crashed_result = destination_session.sequences.set_crashed(
            path, exception, stop_time=stats.stop_time
        )
        assert not is_failure_type(crashed_result, PathNotFoundError)
        assert not is_failure_type(crashed_result, PathIsNotSequenceError)
        assert not is_failure_type(crashed_result, InvalidStateTransitionError)
        assert_type(crashed_result, Success[None])
    else:
        assert_never(state)  # type: ignore[reportArgumentType]

    return Success(None)

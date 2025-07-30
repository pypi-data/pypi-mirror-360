from __future__ import annotations

import contextlib
import copy
from collections.abc import AsyncGenerator, AsyncIterable, Mapping
from typing import Optional

import anyio
import anyio.to_process

from caqtus.device import DeviceConfiguration, DeviceName
from caqtus.session import (
    ExperimentSessionMaker,
    PureSequencePath,
    TracebackSummary,
)
from caqtus.session._shot_id import ShotId
from caqtus.shot_compilation import (
    DeviceCompiler,
    SequenceContext,
)
from caqtus.types.parameter import ParameterNamespace
from caqtus.types.recoverable_exceptions import split_recoverable
from caqtus.types.timelane.timelane import TimeLanes
from caqtus.utils.result import unwrap
from caqtus.utils.result._result import is_failure

from ...types.iteration import StepsConfiguration
from ...types.iteration._step_context import StepContext
from ..device_manager_extension import DeviceManagerExtensionProtocol
from ._logger import logger
from ._shot_compiler import ShotCompilerFactory, create_shot_compiler
from ._shot_runner import ShotRunnerFactory, create_shot_runner
from .sequence_runner import execute_steps
from .shots_manager import ShotData, ShotManager, ShotRetryConfig, ShotScheduler


async def run_sequence(
    sequence: PureSequencePath,
    session_maker: ExperimentSessionMaker,
    shot_retry_config: Optional[ShotRetryConfig],
    global_parameters: Optional[ParameterNamespace],
    device_configurations: Optional[Mapping[DeviceName, DeviceConfiguration]],
    device_manager_extension: DeviceManagerExtensionProtocol,
    shot_runner_factory: ShotRunnerFactory = create_shot_runner,
    shot_compiler_factory: ShotCompilerFactory = create_shot_compiler,
) -> None:
    """Manages the execution of a sequence.

    Args:
        sequence: The sequence to run.

        session_maker: A factory for creating experiment sessions.
            This is used to connect to the storage in which to find the sequence.

        shot_retry_config: Specifies how to retry a shot if an error occurs.
            If an error occurs when the shot runner is running a shot, it will be caught
            by the sequence manager and the shot will be retried according to the
            configuration in this object.

        global_parameters: The global parameters to use to run the sequence.

            These parameters will be saved as the global parameters for the sequence
            when it is prepared.

            If None, the sequence manager will use the default global parameters stored
            in the session.

        device_configurations: The device configurations to use to run the sequence.

            These configurations will be saved as the configurations used for the
            sequence when it is prepared.

            If None, the sequence manager will use the default device configurations.

        device_manager_extension: Used to instantiate the device components.

        shot_runner_factory: A function that can be used to create an object to run
            shots.

        shot_compiler_factory: A function that can be used to create an object to
            compile shots.
    """

    sequence_manager = SequenceManager(
        sequence=sequence,
        session_maker=session_maker,
        shot_retry_config=shot_retry_config,
        global_parameters=global_parameters,
        device_configurations=device_configurations,
        device_manager_extension=device_manager_extension,
        shot_runner_factory=shot_runner_factory,
        shot_compiler_factory=shot_compiler_factory,
    )

    if not isinstance(sequence_manager.sequence_iteration, StepsConfiguration):
        raise NotImplementedError("Only steps iterations is supported for now.")
    async with sequence_manager.run_sequence() as shot_scheduler:
        assert sequence_manager.sequence_context is not None
        initial_context = StepContext(
            sequence_manager.sequence_context.get_parameter_schema().constant_schema
        )
        await execute_steps(
            sequence_manager.sequence_iteration,
            initial_context,
            shot_scheduler,
        )


class SequenceManager:
    def __init__(
        self,
        sequence: PureSequencePath,
        session_maker: ExperimentSessionMaker,
        shot_retry_config: Optional[ShotRetryConfig],
        global_parameters: Optional[ParameterNamespace],
        device_configurations: Optional[Mapping[DeviceName, DeviceConfiguration]],
        device_manager_extension: DeviceManagerExtensionProtocol,
        shot_runner_factory: ShotRunnerFactory,
        shot_compiler_factory: ShotCompilerFactory,
    ) -> None:
        self._session_maker = session_maker
        self._sequence_path = sequence
        self._shot_retry_config = shot_retry_config or ShotRetryConfig()

        with self._session_maker() as session:
            if device_configurations is None:
                self.device_configurations = dict(session.default_device_configurations)
            else:
                self.device_configurations = dict(device_configurations)
            if global_parameters is None:
                self.sequence_parameters = session.get_global_parameters()
            else:
                self.sequence_parameters = copy.deepcopy(global_parameters)

            # It is critical to lock the sequence state by setting it to PREPARING in
            # the same transaction that retrieves the sequence configuration.
            # Otherwise, it can happen that we retrieve the sequence configuration while
            # it is still draft, and it can be modified by another process before we
            # set it to preparing.
            session.sequences.set_preparing(
                self._sequence_path,
                self.device_configurations,
                self.sequence_parameters,
            )
            self.sequence_iteration = session.sequences.get_iteration_configuration(
                sequence
            )
            time_lanes = session.sequences.get_time_lanes(self._sequence_path)
            if is_failure(time_lanes):
                raise time_lanes.exception()
            self.time_lanes: TimeLanes = time_lanes

        self.sequence_context: SequenceContext | None = None

        self._device_manager_extension = device_manager_extension
        self._device_compilers: dict[DeviceName, DeviceCompiler] = {}

        self._shot_runner_factory = shot_runner_factory
        self._shot_compiler_factory = shot_compiler_factory

    @contextlib.asynccontextmanager
    async def run_sequence(self) -> AsyncGenerator[ShotScheduler, None]:
        """Run background tasks to compile and run shots for a given sequence.

        Returns:
            A asynchronous context manager that yields a shot scheduler object.

            When the context manager is entered, it will set the sequence to PREPARING
            while acquiring the necessary resources and the transition to RUNNING.

            The context manager will yield a shot scheduler object that can be used to
            push shots to the sequence execution queue.
            When a shot is done, its associated data will be stored in the associated
            sequence.

            One shot scheduling is over, the context manager will be exited.
            At this point is will finish the sequence and transition the sequence state
            to FINISHED when the sequence terminated normally, CRASHED if an error
            occurred or INTERRUPTED if the sequence was interrupted by the user.
        """

        try:
            self.sequence_context = SequenceContext._new(
                self.device_configurations,
                self.sequence_iteration,
                self.sequence_parameters,
                self.time_lanes,
            )
            shot_compiler = self._shot_compiler_factory(
                self.sequence_context,
                self._device_manager_extension,
            )

            # We start the subprocesses while preparing the sequence to avoid
            # the overhead of starting when the sequence is launched.
            async with anyio.create_task_group() as tg:
                for _ in range(4):
                    tg.start_soon(anyio.to_process.run_sync, nothing)
            async with (
                self._shot_runner_factory(
                    self.sequence_context, shot_compiler, self._device_manager_extension
                ) as shot_runner,
                ShotManager(
                    shot_runner,
                    shot_compiler,
                    self._shot_retry_config,
                ) as (
                    scheduler_cm,
                    data_stream_cm,
                ),
            ):
                with self._session_maker() as session:
                    session.sequences.set_running(self._sequence_path, start_time="now")
                async with (
                    anyio.create_task_group() as tg,
                    scheduler_cm as scheduler,
                ):
                    tg.start_soon(self._store_shots, data_stream_cm)
                    yield scheduler
        except* anyio.get_cancelled_exc_class():
            with self._session_maker() as session:
                session.sequences.set_interrupted(self._sequence_path, stop_time="now")
            raise
        except* BaseException as e:
            tb_summary = TracebackSummary.from_exception(e)
            with self._session_maker() as session:
                unwrap(
                    session.sequences.set_crashed(
                        self._sequence_path, tb_summary, stop_time="now"
                    )
                )
            recoverable, non_recoverable = split_recoverable(e)
            if non_recoverable:
                raise
            if recoverable:
                logger.warning(
                    "A recoverable error occurred while running the sequence.",
                    exc_info=recoverable,
                )

        else:
            with self._session_maker() as session:
                session.sequences.set_finished(self._sequence_path, stop_time="now")

    async def _store_shots(
        self,
        data_stream_cm: contextlib.AbstractAsyncContextManager[AsyncIterable[ShotData]],
    ):
        async with data_stream_cm as shots_data:
            async for shot_data in shots_data:
                await self._store_shot(shot_data)

    async def _store_shot(self, shot_data: ShotData) -> None:
        params = {
            name: value for name, value in shot_data.variables.to_flat_dict().items()
        }
        async with self._session_maker.async_session() as session:
            result = await session.sequences.create_shot(
                ShotId(self._sequence_path, shot_data.index),
                params,
                shot_data.data,
                shot_data.start_time,
                shot_data.end_time,
            )
            unwrap(result)


def nothing():
    pass

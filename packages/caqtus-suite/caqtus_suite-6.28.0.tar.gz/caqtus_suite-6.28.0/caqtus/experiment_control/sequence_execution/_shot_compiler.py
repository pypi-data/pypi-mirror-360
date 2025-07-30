from __future__ import annotations

import abc
import pickle
from collections.abc import Callable, Mapping
from typing import Any, Protocol

import anyio.to_process
import attrs

from caqtus.device import DeviceName
from caqtus.shot_compilation import (
    DeviceCompiler,
    DeviceNotUsedException,
    SequenceContext,
)
from caqtus.shot_compilation.compilation_contexts import ShotContext
from caqtus.types._parameter_namespace import VariableNamespace
from caqtus.types.recoverable_exceptions import InvalidValueError
from caqtus.utils._tblib import ensure_exception_pickling

from ..device_manager_extension import DeviceManagerExtensionProtocol
from ._shot_primitives import ShotParameters


class ShotCompilerProtocol(Protocol):
    @abc.abstractmethod
    def compile_initialization_parameters(
        self,
    ) -> Mapping[DeviceName, Mapping[str, Any]]:
        """Compile the initialization parameters for the devices.

        Returns:
            A mapping from device names to the initialization parameters for each
            device.

            The keys of the mapping are the device names that are in use for this
            sequence.
        """

        raise NotImplementedError

    @abc.abstractmethod
    async def compile_shot(
        self, shot_parameters: ShotParameters
    ) -> tuple[Mapping[DeviceName, Mapping[str, Any]], float]:
        raise NotImplementedError


type ShotCompilerFactory = Callable[
    [SequenceContext, DeviceManagerExtensionProtocol], ShotCompilerProtocol
]


class ShotCompiler(ShotCompilerProtocol):
    def __init__(
        self,
        sequence_context: SequenceContext,
        device_compilers: Mapping[DeviceName, DeviceCompiler],
    ):
        self._sequence_context = sequence_context
        self.device_compilers = device_compilers
        self.pickled_context = pickle.dumps(
            CompilationContext(
                sequence_context=self._sequence_context,
                device_compilers=device_compilers,
            )
        )

    def compile_initialization_parameters(
        self,
    ) -> Mapping[DeviceName, Mapping[str, Any]]:
        initialization_parameters = {}
        for device_name, compiler in self.device_compilers.items():
            initialization_parameters[device_name] = (
                compiler.compile_initialization_parameters()
            )
        return initialization_parameters

    async def compile_shot(
        self, shot_parameters: ShotParameters
    ) -> tuple[Mapping[DeviceName, Mapping[str, Any]], float]:
        # We add a deadline to shot compilation to not hang indefinitely in case of
        # a bug.
        with anyio.move_on_after(10):
            # Here we send to the other process the pre-pickled compilation context and
            # the shot parameters.
            # It is important that we pickle the context only once and not for every
            # shot as it can take a long time to pickle and block the event loop.
            return await anyio.to_process.run_sync(
                compile_shot_sync,
                self.pickled_context,
                shot_parameters.parameters,
                cancellable=True,
            )
        raise TimeoutError(
            "Shot compilation took too long to complete and has been terminated."
        )


@attrs.frozen
class CompilationContext:
    sequence_context: SequenceContext = attrs.field()
    device_compilers: Mapping[DeviceName, DeviceCompiler] = attrs.field()


@ensure_exception_pickling
def compile_shot_sync(
    pickled_compilation_context: bytes,
    shot_parameters: VariableNamespace,
) -> tuple[Mapping[DeviceName, Mapping[str, Any]], float]:
    compilation_context = pickle.loads(pickled_compilation_context)
    assert isinstance(compilation_context, CompilationContext)
    shot_context = ShotContext(
        sequence_context=compilation_context.sequence_context,  # pyright: ignore[reportCallIssue]
        variables=shot_parameters.dict(),  # pyright: ignore[reportCallIssue]
        device_compilers=compilation_context.device_compilers,  # pyright: ignore[reportCallIssue]
    )

    results = {}
    for device_name in compilation_context.device_compilers:
        results[device_name] = shot_context.get_shot_parameters(device_name)

    # noinspection PyProtectedMember
    if unused_lanes := shot_context._unused_lanes():
        raise InvalidValueError(
            "The following lanes where not used during the shot: "
            + ", ".join(unused_lanes)
        )

    return results, float(shot_context.get_shot_duration())


def create_shot_compiler(
    initial_sequence_context: SequenceContext,
    device_manager_extension: DeviceManagerExtensionProtocol,
) -> ShotCompiler:
    device_compilers = create_device_compilers(
        initial_sequence_context, device_manager_extension
    )
    in_use_configurations = {
        device_name: initial_sequence_context.get_device_configuration(device_name)
        for device_name in device_compilers
    }
    shot_compiler = _create_shot_compiler(
        initial_sequence_context._with_devices(in_use_configurations),
        device_compilers=device_compilers,
    )
    return shot_compiler


def create_device_compilers(
    sequence_context: SequenceContext,
    device_manager_extension: DeviceManagerExtensionProtocol,
) -> dict[DeviceName, DeviceCompiler]:
    device_compilers = {}
    for (
        device_name,
        device_configuration,
    ) in sequence_context.get_all_device_configurations().items():
        compiler_type = device_manager_extension.get_device_compiler_type(
            device_configuration
        )
        try:
            compiler = compiler_type(device_name, sequence_context)
        except DeviceNotUsedException:
            continue
        else:
            device_compilers[device_name] = compiler
    return device_compilers


def _create_shot_compiler(
    sequence_context: SequenceContext,
    device_compilers: Mapping[DeviceName, DeviceCompiler],
) -> ShotCompiler:
    shot_compiler = ShotCompiler(
        sequence_context,
        device_compilers=device_compilers,
    )
    return shot_compiler

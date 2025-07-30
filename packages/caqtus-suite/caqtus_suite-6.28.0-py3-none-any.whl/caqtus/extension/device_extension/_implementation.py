from __future__ import annotations

from collections.abc import Callable
from typing import Generic

import attrs

from caqtus.device import DeviceConfiguration, Device, DeviceController
from caqtus.device.configuration import DeviceConfigType as DeviceConfigT
from caqtus.device.remote import DeviceProxy
from caqtus.gui.condetrol.device_configuration_editors import DeviceConfigurationEditor
from caqtus.shot_compilation import DeviceCompiler
from caqtus.utils.serialization import JSON


@attrs.frozen(kw_only=True)
class DeviceExtension(Generic[DeviceConfigT]):
    """Define how to implement a device plugin.

    This class is generic in the :class:`DeviceConfiguration` type.

    Attributes:
        label: A human-readable label for the type of device represented by this
            extension.

            This label describes the type of device and will be displayed to the user
            when they are selecting a device to add to the experiment.

            No two device extensions should have the same label.

        configuration_type: The type of configuration used to store the settings of
            the device.

            The name of the type is used to identify the configuration type in the
            storage.
            It is thus not recommended to change the name of the type after it has been
            used in the application, as the new name will not be recognized as the same
            type.

        configuration_factory: A factory function that returns a new instance of the
            configuration type.

            This function will be called when a new device of this type is added to the
            experiment.
            It should return a default instance of the configuration type.

        configuration_dumper: A function that converts a configuration instance to a
            JSON-serializable format.
            This function will be used to save the configuration.

        configuration_loader: A function that converts a JSON-serializable format to a
            configuration instance.
            This function will be used to load the configuration.
            It is passed the JSON-serializable format saved by the
            `configuration_dumper` function.

        editor_type: A function that creates an editor for the device configuration.

            When the user wants to edit the configuration of a device of this type,
            this function will be called to create an editor for the configuration.
            The function is passed as argument the configuration instance to edit.

            Once the user has finished editing the configuration, the method
            :meth:`~caqtus.gui.condetrol.device_configuration_editors.DeviceConfigurationEditor.get_configuration`
            of the editor is called and the result is saved.

        device_type: A callable that returns a new device instance.

            This function will be called when a device associated with this extension
            needs to be created.
            The arguments passed are obtained by calling the method
            :meth:`caqtus.device.compiler.DeviceCompiler.compile_initialization_parameters`
            of the compiler associated with the device.

            This function needs to be pickleable as it will be sent to a remote process.

        compiler_type: The type of compiler used to compile the parameters of the
            device.

            When the sequence is launched, a compiler will be created for each device
            configuration. The compiler
            :meth:`~caqtus.shot_compilation.DeviceCompiler.__init__` method is
            called with the name of the device and the context of the sequence.
            If the initialization method raises :class:`DeviceNotUsedException`, no
            further actions will be taken for this device, and it will be ignored for
            the sequence.

            The method
            :meth:`~caqtus.shot_compilation.DeviceCompiler.compile_initialization_parameters`
            is called at the beginning of the sequence to get the parameters to
            pass to the :attr:`device_type` function to create the device.

            The method
            :meth:`~caqtus.shot_compilation.DeviceCompiler.compile_shot_parameters` is
            then called for each shot to get the parameters to pass to the device
            controller for the shot.

            Warning:
                The compilation of each shot happens in a new process using each time a
                new copy of the compiler.
                This has some consequences:

                - The compiler should be pickleable.
                - If the compiler is modified during the compilation of a shot, the
                  changes will not be reflected in the next shot.
                - :func:`print` statements in the compiler will not be displayed in the
                  console.

    """

    label: str = attrs.field(converter=str)

    configuration_type: type[DeviceConfigT] = attrs.field()
    configuration_factory: Callable[[], DeviceConfigT] = attrs.field()
    configuration_dumper: Callable[[DeviceConfigT], JSON] = attrs.field()
    configuration_loader: Callable[[JSON], DeviceConfigT] = attrs.field()

    editor_type: Callable[[DeviceConfigT], DeviceConfigurationEditor[DeviceConfigT]] = (
        attrs.field()
    )

    device_type: Callable[..., Device] = attrs.field()
    compiler_type: type[DeviceCompiler] = attrs.field()
    controller_type: type[DeviceController] = attrs.field()
    proxy_type: type[DeviceProxy] = attrs.field()

    @configuration_type.validator  # type: ignore
    def _validate_configuration_type(self, _, value):
        if not issubclass(value, DeviceConfiguration):
            raise ValueError(f"Invalid configuration type: {value}.")

    @compiler_type.validator  # type: ignore
    def _validate_compiler_type(self, _, value):
        if not issubclass(value, DeviceCompiler):
            raise ValueError(f"Invalid compiler type: {value}.")

    @controller_type.validator  # type: ignore
    def _validate_controller_type(self, _, value):
        if not issubclass(value, DeviceController):
            raise ValueError(f"Invalid controller type: {value}.")

    @proxy_type.validator  # type: ignore
    def _validate_proxy_type(self, _, value):
        if not issubclass(value, DeviceProxy):
            raise ValueError(f"Invalid proxy type: {value}.")

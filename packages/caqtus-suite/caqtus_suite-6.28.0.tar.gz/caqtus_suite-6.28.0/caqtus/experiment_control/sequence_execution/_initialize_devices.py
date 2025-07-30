import contextlib
from collections.abc import Mapping, AsyncGenerator, Callable
from typing import TypeVar, Any

from caqtus.device import DeviceName, Device, DeviceConfiguration
from caqtus.device.remote import DeviceProxy, RPCConfiguration
from caqtus.device.remote.rpc import RPCClient
from caqtus.experiment_control.device_manager_extension import (
    DeviceManagerExtensionProtocol,
)
from caqtus.experiment_control.sequence_execution._async_utils import (
    task_group_with_error_message,
)
from caqtus.formatter import fmt, device
from caqtus.types.recoverable_exceptions import ConnectionFailedError


@contextlib.asynccontextmanager
async def create_devices(
    initialization_parameters: Mapping[DeviceName, Mapping[str, Any]],
    device_configs: Mapping[DeviceName, DeviceConfiguration],
    device_types: Mapping[DeviceName, Callable[..., Device]],
    device_manager_extension: DeviceManagerExtensionProtocol,
) -> AsyncGenerator[Mapping[DeviceName, DeviceProxy], None]:
    device_server_configs = {}
    device_to_server = {}
    for device_name, device_config in device_configs.items():
        remote_server = device_config.remote_server
        if remote_server is not None:
            device_server_configs[remote_server] = (
                device_manager_extension.get_device_server_config(remote_server)
            )
            device_to_server[device_name] = remote_server

    async with create_rpc_clients(
        device_to_server, device_server_configs
    ) as rpc_clients:
        uninitialized_proxies = {}
        for device_name, init_params in initialization_parameters.items():
            device_config = device_configs[device_name]
            device_type = device_types[device_name]
            if device_config.remote_server is None:
                raise NotImplementedError(
                    f"Can't have no remote server for {device(device_name)}"
                )
            client = rpc_clients[device_name]
            proxy_type = device_manager_extension.get_proxy_type(device_config)
            device_proxy = proxy_type(client, device_type, **init_params)
            uninitialized_proxies[device_name] = device_proxy
        async with context_group(uninitialized_proxies) as devices:
            yield devices


@contextlib.asynccontextmanager
async def create_rpc_clients(
    device_servers: Mapping[DeviceName, str],
    device_server_configs: Mapping[str, RPCConfiguration],
) -> AsyncGenerator[dict[DeviceName, RPCClient], None]:
    clients: dict[DeviceName, RPCClient] = {}
    async with contextlib.AsyncExitStack() as stack:
        for device_name, server in device_servers.items():
            config = device_server_configs[server]
            client = RPCClient(config.host, config.port)
            try:
                await stack.enter_async_context(client)
            except OSError as e:
                raise ConnectionFailedError(
                    fmt(
                        "Failed to connect to {:device server} for {:device}",
                        server,
                        device_name,
                    )
                ) from e
            clients[device_name] = client
        yield clients


T = TypeVar("T")


async def enter_and_push[
    K, T
](
    stack: contextlib.AsyncExitStack,
    device: K,
    cm: contextlib.AbstractAsyncContextManager[T],
    results: dict[K, T],
):
    try:
        value = await stack.enter_async_context(cm)
    except Exception as e:
        raise RuntimeError(fmt("Failed to initialize {:device}", device)) from e
    results[device] = value


@contextlib.asynccontextmanager
async def context_group[
    K, T
](cms: Mapping[K, contextlib.AbstractAsyncContextManager[T]]) -> AsyncGenerator[
    Mapping[K, T], None
]:
    results = {}
    async with contextlib.AsyncExitStack() as stack:
        async with task_group_with_error_message(
            "Errors occurred while initializing devices"
        ) as tg:
            for key, cm in cms.items():
                tg.start_soon(enter_and_push, stack, key, cm, results)
        yield results

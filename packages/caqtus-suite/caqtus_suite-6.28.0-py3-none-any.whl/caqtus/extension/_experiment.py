import contextlib
import ctypes
import logging.config
import platform
import warnings
from collections.abc import Callable
from typing import Optional, assert_never, Concatenate

from typing_extensions import deprecated

from caqtus.experiment_control.manager import (
    LocalExperimentManager,
    RemoteExperimentManagerClient,
    RemoteExperimentManagerServer,
)

# noinspection PyProtectedMember
from caqtus.gui.condetrol._condetrol import Condetrol
from caqtus.session.sql import (
    PostgreSQLConfig,
    PostgreSQLStorageManager,
    SQLiteConfig,
    SQLiteStorageManager,
    SQLStorageManager,
)
from ._caqtus_extension import CaqtusExtension
from .device_extension import DeviceExtension
from .time_lane_extension import TimeLaneExtension
from ..device.configuration import DeviceServerName
from ..device.remote import Server, RPCConfiguration
from ..experiment_control import ExperimentManager
from ..experiment_control.manager import (
    ExperimentManagerConnection,
    LocalExperimentManagerConfiguration,
    RemoteExperimentManagerConfiguration,
)
from ..experiment_control.sequence_execution import ShotRetryConfig
from ..session import ExperimentSession, StorageManager
from ..session.sql._serializer import SerializerProtocol


class Experiment:
    """Configure parameters and register extensions for a specific experiment.

    There should be only a single instance of this class in the entire application.
    It is used to configure the experiment and knows how to launch the different
    components of the application after it has been configured.

    Args:
        storage_config: The configuration of the storage backend to be used to store the
            data of the experiment.
    """

    def __init__(
        self, storage_config: PostgreSQLConfig | SQLiteConfig | None = None
    ) -> None:
        if storage_config is None:
            warnings.warn(
                "A storage configuration should be passed when initializing the "
                "experiment.",
                DeprecationWarning,
                stacklevel=2,
            )
        self._storage_config: PostgreSQLConfig | SQLiteConfig | None = storage_config
        self._extension = CaqtusExtension()
        self._experiment_manager: Optional[LocalExperimentManager] = None
        self._experiment_manager_location: ExperimentManagerConnection = (
            LocalExperimentManagerConfiguration()
        )
        self._shot_retry_config: Optional[ShotRetryConfig] = None

    def setup_default_extensions(self) -> None:
        """Register some commonly used extensions to this experiment.

        This method registers the following extensions:

        * digital time lanes
        * analog time lanes
        * camera time lanes
        """

        from caqtus.extension.time_lane_extension import (
            digital_time_lane_extension,
            analog_time_lane_extension,
            camera_time_lane_extension,
        )

        self.register_time_lane_extension(digital_time_lane_extension)
        self.register_time_lane_extension(analog_time_lane_extension)
        self.register_time_lane_extension(camera_time_lane_extension)

    @deprecated(
        "Pass the configuration directly to the Experiment() constructor instead."
    )
    def configure_storage(
        self, storage_config: PostgreSQLConfig | SQLiteConfig
    ) -> None:
        """Configure the storage backend to be used by the application.

        After this method is called, the application will read and write data and
        configurations to the storage specified.

        It is necessary to call this method before launching the application.

        Warning:
            Calling this method multiple times will overwrite the previous
            configuration.
        """

        if self._storage_config is not None:
            warnings.warn("Storage configuration is being overwritten.", stacklevel=2)
        self._storage_config = storage_config

    def configure_shot_retry(
        self, shot_retry_config: Optional[ShotRetryConfig]
    ) -> None:
        """Configure the shot retry policy to be used when running sequences.

        After this method is called, shots that raise errors will be retried according
        to the policy specified.

        It is necessary to call this method before launching the experiment manager.

        Warning:
            Calling this method multiple times will overwrite the previous
            configuration.
        """

        self._shot_retry_config = shot_retry_config

    def configure_experiment_manager(
        self, location: ExperimentManagerConnection
    ) -> None:
        """Configure the location of the experiment manager with respect to Condetrol.

        The :class:`ExperimentManager` is responsible for running sequences on the
        experiment.

        It can be either running in the same process as the Condetrol application or in
        a separate process.

        This is configured by passing an instance of either
        :class:`LocalExperimentManagerConfiguration` or
        :class:`RemoteExperimentManagerConfiguration`.

        If this method is not called, the experiment manager will be assumed to be
        running in the same local process as the Condetrol application.

        If the experiment manager is configured to run in the same process, it will be
        created when the Condetrol application is launched.
        An issue with this approach is that if the Condetrol application crashes, the
        experiment manager will also stop abruptly, potentially leaving the experiment
        in an undesired state.

        If the experiment manager is configured to run in a separate process, it will be
        necessary to have an experiment manager server running before launching the
        Condetrol application.
        The Condetrol application will then connect to the server and transmit the
        commands to the other process.
        If the Condetrol application crashes, the experiment manager will be unaffected.

        Warning:
            Calling this method multiple times will overwrite the previous
            configuration.
        """

        self._experiment_manager_location = location

    def register_device_extension(self, device_extension: DeviceExtension) -> None:
        """Register a new device extension.

        After this method is called, the device extension will be available to the
        application, both in the device editor tab in Condetrol and while running the
        experiment.
        """

        self._extension.register_device_extension(device_extension)

    def register_time_lane_extension(
        self, time_lane_extension: TimeLaneExtension
    ) -> None:
        """Register a new time lane extension.

        After this method is called, the time lane extension will be available to the
        application, both in the time lane editor tab in Condetrol and while running the
        experiment.
        """

        self._extension.register_time_lane_extension(time_lane_extension)

    def register_device_server(
        self, name: DeviceServerName, config: RPCConfiguration
    ) -> None:
        """Register a new device server.

        After this method is called, the device server will be available to the
        application to connect to devices.
        """

        self._extension.register_device_server_config(name, config)

    def get_storage_manager(self) -> StorageManager:
        """Get the storage manager to be used by the application.

        The storage manager is responsible for interacting with the storage of the
        experiment.
        """

        return self._get_storage_manager(check_schema=True)

    @deprecated("Use get_storage_manager instead.")
    def get_session_maker(self) -> StorageManager:
        return self.get_storage_manager()

    def build_storage_manager[T: StorageManager, **P](
        self,
        backend_type: Callable[Concatenate[SerializerProtocol, P], T],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:
        """Create and set up a storage manager with the current registered extensions.

        Args:
            backend_type: Defines how the data will be stored.
            *args: The arguments to pass to the storage backend constructor.
            **kwargs: The keyword arguments to pass to the storage backend constructor.
        """

        storage_backend_manager = self._build_storage_manager(
            backend_type,
            *args,
            **kwargs,
        )
        if isinstance(storage_backend_manager, SQLStorageManager):
            storage_backend_manager.check()

        return storage_backend_manager

    def _build_storage_manager[T: StorageManager, **P](
        self,
        backend_type: Callable[Concatenate[SerializerProtocol, P], T],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:
        return self._extension.create_session_maker(
            backend_type,
            *args,
            **kwargs,
        )

    def _get_storage_manager(self, check_schema: bool = True) -> StorageManager:
        if self._storage_config is None:
            error = RuntimeError("Storage configuration has not been set.")
            error.add_note(
                "Pass the storage configuration to the Experiment() constructor."
            )
            raise error
        if isinstance(self._storage_config, SQLiteConfig):
            storage_manager = self._build_storage_manager(
                SQLiteStorageManager,
                config=self._storage_config,
            )
        elif isinstance(self._storage_config, PostgreSQLConfig):
            storage_manager = self._build_storage_manager(
                PostgreSQLStorageManager,
                config=self._storage_config,
            )
        else:
            assert_never(self._storage_config)
        if check_schema:
            storage_manager.check()
        return storage_manager

    def connect_to_experiment_manager(self) -> ExperimentManager:
        """Connect to the experiment manager."""

        location = self._experiment_manager_location
        if isinstance(location, LocalExperimentManagerConfiguration):
            return self.get_local_experiment_manager()
        elif isinstance(location, RemoteExperimentManagerConfiguration):
            client = RemoteExperimentManagerClient(
                address=(location.address, location.port),
                authkey=bytes(location.authkey, "utf-8"),
            )
            return client.get_experiment_manager()
        else:
            assert_never(location)

    def get_local_experiment_manager(self) -> LocalExperimentManager:
        """Return the local experiment manager.

        This method is used to create an instance of the experiment manager that runs
        in the local process.

        The first time this method is called, the experiment manager will be created.
        If it is called again, the instance previously created will be returned.
        """

        if self._experiment_manager is None:
            self._experiment_manager = LocalExperimentManager(
                session_maker=self.get_storage_manager(),
                device_manager_extension=self._extension.device_manager_extension,
                shot_retry_config=self._shot_retry_config,
            )
        return self._experiment_manager

    def launch_condetrol(self) -> None:
        """Launch the Condetrol application.

        The Condetrol application is the main user interface to the experiment.
        It allows to edit and launch sequences, as well as edit the device
        configurations.
        """

        if platform.system() == "Windows":
            # This is necessary to use the UI icon in the taskbar and not the default
            # Python icon.
            app_id = "caqtus.condetrol"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)  # type: ignore[reportAttributeAccessIssue]

        app = Condetrol(
            self.get_storage_manager(),
            extension=self._extension.condetrol_extension,
            connect_to_experiment_manager=self.connect_to_experiment_manager,
        )
        try:
            app.run()
        except:
            logging.exception("An error occurred.", exc_info=True)
            raise

    def launch_experiment_server(self) -> None:
        """Launch the experiment server.

        The experiment server is used to run procedures on the experiment manager from a
        remote process.

        If the environment variable `CAQTUS_BLOCKING_TASK_DURATION_WARNING` is set to
        a float duration in seconds, a warning will be logged if a task doesn't yield to
        the event loop for that duration during the execution of a sequence.
        """

        if platform.system() == "Windows":
            # This is necessary to use the UI icon in the taskbar and not the default
            # Python icon.
            app_id = "caqtus.experiment_server"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)  # type: ignore[reportAttributeAccessIssue]

        if not isinstance(
            self._experiment_manager_location, RemoteExperimentManagerConfiguration
        ):
            error = RuntimeError(
                "The experiment manager is not configured to run remotely."
            )
            error.add_note(
                "Please call `configure_experiment_manager` with a remote "
                "configuration."
            )
            raise error

        server = RemoteExperimentManagerServer(
            session_maker=self.get_storage_manager(),
            address=("localhost", self._experiment_manager_location.port),
            authkey=bytes(self._experiment_manager_location.authkey, "utf-8"),
            shot_retry_config=self._shot_retry_config,
            device_manager_extension=self._extension.device_manager_extension,
        )

        with server:
            print("Ready")
            server.serve_forever()

    @staticmethod
    def launch_device_server(
        config: RPCConfiguration, name: str = "device_server"
    ) -> None:
        """Launch a device server in the current process.

        This method will block until the server is stopped.

        Args:
            config: The configuration of the server.
            name: The name of the server. It is used to create the log file.
        """

        if platform.system() == "Windows":
            # This is necessary to use the UI icon in the taskbar and not the default
            # Python icon.
            app_id = "caqtus.device_server"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)  # type: ignore[reportAttributeAccessIssue]

        with Server(config) as server:
            print("Ready")
            server.wait_for_termination()

    def storage_session(self) -> contextlib.AbstractContextManager[ExperimentSession]:
        """Return a context manager that provides a session to the storage backend.

        A session can be used to access the data stored in the experiment.
        """

        return self.get_storage_manager().session()

    def upgrade_database(self) -> None:
        """Upgrade the database schema of the experiment to the latest version.

        .. Warning::

            If the database contains important data, it is strongly recommended to
            back it up before running this function in case something goes wrong.
        """

        upgrade_database(self)


def upgrade_database(experiment: Experiment) -> None:
    """Upgrade the database schema of the experiment to the latest version.

    .. Warning::

        It is strongly recommended to back up the database before running this
        function in case something goes wrong.

    Args:
        experiment: The experiment to upgrade the database for.
            It must have been configured with a PostgreSQL storage backend.
    """

    storage_manager = experiment._get_storage_manager(check_schema=False)
    if not isinstance(storage_manager, SQLStorageManager):
        error = RuntimeError("The storage manager is not a SQL storage manager.")
        error.add_note(
            "The upgrade_database method is only available for SQL storage managers."
        )
        raise error
    storage_manager.upgrade()


def stamp_database(experiment: Experiment) -> None:
    """Mark old databases schema with the original revision.

    This should only be called on databases that were created before version 6.3.0.
    """

    from alembic.command import stamp

    storage_manager = experiment._get_storage_manager(check_schema=False)
    if not isinstance(storage_manager, PostgreSQLStorageManager):
        raise RuntimeError("The storage manager is not a PostgreSQL storage manager.")
    config = storage_manager._get_alembic_config()

    stamp(config, "038164d73465")

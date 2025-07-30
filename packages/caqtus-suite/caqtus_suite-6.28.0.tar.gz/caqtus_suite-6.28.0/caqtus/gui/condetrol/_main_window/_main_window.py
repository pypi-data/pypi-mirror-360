from __future__ import annotations

import contextlib
import functools
import math
import platform
from collections.abc import Callable, Awaitable
from typing import Never

import anyio
import anyio.abc
import anyio.to_thread
from PySide6 import QtGui, QtCore, QtWidgets
from PySide6.QtCore import Qt

from caqtus.__about__ import __version__
from caqtus.experiment_control.manager import ExperimentManager, Procedure
from caqtus.session import ExperimentSessionMaker, PureSequencePath, TracebackSummary
from caqtus.types.parameter import ParameterNamespace
from caqtus.types.recoverable_exceptions import (
    split_recoverable,
)
from ._main_window_ui import Ui_CondetrolMainWindow
from .._extension import CondetrolExtensionProtocol
from .._logger import logger
from .._parameter_tables_editor import ParameterNamespaceEditor
from .._path_view import EditablePathHierarchyView
from .._sequence_widget import SequenceWidget
from .._sequence_widget.sequence_widget import (
    _query_state_sync,
    synchronize_editor_and_storage,
    synchronize_sequence_widget,
)
from ..device_configuration_editors._configurations_editor import (
    DeviceConfigurationsDialog,
)
from ..._common.exception_tree import ExceptionDialog
from ..._common.waiting_widget import run_with_wip_widget
from ...qtutil import temporary_widget


class CondetrolWindowHandler:
    def __init__(
        self, main_window: CondetrolMainWindow, session_maker: ExperimentSessionMaker
    ):
        self.main_window = main_window
        self.session_maker = session_maker
        self.task_group = anyio.create_task_group()
        self.is_running_sequence = False

        self.main_window.path_view.sequence_start_requested.connect(self.start_sequence)
        self.main_window.sequence_widget.sequence_start_requested.connect(
            self.start_sequence
        )
        self.background_sequence_synchronization = BackgroundTask(
            synchronize_sequence_widget,
            100e-3,
            self.main_window.sequence_widget,
            self.session_maker,
        )

    async def run_async(self) -> None:
        """Run the main window asynchronously."""

        async with self.task_group:
            self.task_group.start_soon(self.main_window.path_view.run_async)
            self.task_group.start_soon(self._monitor_global_parameters)
            self.task_group.start_soon(self.background_sequence_synchronization.run)

    async def _monitor_global_parameters(self) -> None:
        while True:
            async with self.session_maker.async_session() as session:
                parameters = await session.get_global_parameters()
            if parameters != self.main_window.global_parameters_editor.get_parameters():
                self.main_window.global_parameters_editor.set_parameters(parameters)
            await anyio.sleep(0.2)

    def start_sequence(self, path: PureSequencePath):
        try:
            experiment_manager = run_with_wip_widget(
                self.main_window,
                "Connecting to experiment manager...",
                self.main_window.connect_to_experiment_manager,
            )
        except Exception as e:
            logger.error("Failed to connect to experiment manager.", exc_info=e)
            self.main_window.display_error(
                "Failed to connect to experiment manager.",
                TracebackSummary.from_exception(e),
            )
            return

        if self.is_running_sequence:
            self.main_window.display_error(
                "A sequence is already running.",
                TracebackSummary.from_exception(
                    RuntimeError("A sequence is already running.")
                ),
            )
            return
        procedure = experiment_manager.create_procedure(
            "sequence launched from GUI", acquisition_timeout=1
        )
        self.task_group.start_soon(self._run_sequence, procedure, path)
        self.is_running_sequence = True

    async def _run_sequence(self, procedure: Procedure, sequence):
        with self.background_sequence_synchronization.suspend():
            async with self.session_maker.async_session() as session:
                await synchronize_editor_and_storage(
                    self.main_window.sequence_widget, session
                )
        with procedure:
            try:
                await anyio.to_thread.run_sync(procedure.start_sequence, sequence)
            except Exception as e:
                exception = RuntimeError(
                    f"An error occurred while starting the sequence {sequence}."
                )
                exception.__cause__ = e
                self.main_window.signal_exception_while_running_sequence(exception)
                return

            while await anyio.to_thread.run_sync(  # noqa: ASYNC110
                procedure.is_running_sequence
            ):
                await anyio.sleep(50e-3)

        self.is_running_sequence = False


class CondetrolMainWindow(QtWidgets.QMainWindow, Ui_CondetrolMainWindow):
    """The main window of the Condetrol GUI.

    Parameters
    ----------
    session_maker
        A callable that returns an ExperimentSession.
        This is used to access the storage in which to look for sequences to display
        and edit.
    connect_to_experiment_manager
        A callable that is called to connect to an experiment manager in charge of
        running sequences.
        This is used to submit sequences to the manager when the user starts them
        in the GUI.
    extension
        The extension that provides the GUI with the necessary tools to edit sequences
        and device configurations.
    """

    def __init__(
        self,
        session_maker: ExperimentSessionMaker,
        connect_to_experiment_manager: Callable[[], ExperimentManager],
        extension: CondetrolExtensionProtocol,
    ):
        super().__init__()
        self.path_view = EditablePathHierarchyView(session_maker, self)
        self.global_parameters_editor = ParameterNamespaceEditor()
        self.connect_to_experiment_manager = connect_to_experiment_manager
        self.session_maker = session_maker
        self.sequence_widget = SequenceWidget(extension.lane_extension, parent=self)
        self.device_configurations_dialog = DeviceConfigurationsDialog(
            extension.device_extension, parent=self
        )

        self.setup_ui()
        self.restore_window()
        self.setup_connections()
        self.timer = QtCore.QTimer(self)

    def setup_ui(self):
        self.setupUi(self)
        self.setCentralWidget(self.sequence_widget)
        paths_dock = QtWidgets.QDockWidget("Sequences", self)
        paths_dock.setObjectName("SequencesDock")
        paths_dock.setWidget(self.path_view)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, paths_dock)
        self.dock_menu.addAction(paths_dock.toggleViewAction())
        global_parameters_dock = QtWidgets.QDockWidget("Global parameters", self)
        global_parameters_dock.setWidget(self.global_parameters_editor)
        global_parameters_dock.setObjectName("GlobalParametersDock")
        self.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea, global_parameters_dock
        )
        self.dock_menu.addAction(global_parameters_dock.toggleViewAction())
        # We hide the global parameters dock by default to reduce clutter when
        # launching the app the first time.
        global_parameters_dock.hide()

    def setup_connections(self):
        self.action_edit_device_configurations.triggered.connect(
            self.open_device_configurations_editor
        )
        self.path_view.sequence_double_clicked.connect(self.set_edited_sequence)
        self.path_view.sequence_interrupt_requested.connect(self.interrupt_sequence)
        self.global_parameters_editor.parameters_edited.connect(
            self._on_global_parameters_edited
        )
        self.about_qt_action.triggered.connect(self._on_about_qt_action_triggered)
        self.about_condetrol_action.triggered.connect(
            self._on_about_condetrol_action_triggered
        )
        self.help_action.triggered.connect(self._on_help_action_triggered)

    def _on_help_action_triggered(self):
        QtGui.QDesktopServices.openUrl(
            QtCore.QUrl(
                "https://caqtus.readthedocs.io/en/latest/reference/condetrol/manual.html"
            )
        )

    def set_edited_sequence(self, path: PureSequencePath):
        with self.session_maker() as session:
            state = _query_state_sync(path, session)
        self.sequence_widget.set_fresh_state(state)

    def on_procedure_exception(self, exception: Exception):
        recoverable, non_recoverable = split_recoverable(exception)
        if recoverable:
            logger.warning(
                "Recoverable exception occurred while running a sequence",
                exc_info=recoverable,
            )
        if non_recoverable:
            # The exception will be logged anyway when condetrol crashes, so we don't
            # need to log it here.
            raise non_recoverable

        assert recoverable is not None

        self.display_error(
            "An error occurred while running a sequence.",
            TracebackSummary.from_exception(recoverable),
        )

    def open_device_configurations_editor(self) -> None:
        with self.session_maker() as session:
            previous_device_configurations = dict(session.default_device_configurations)
        self.device_configurations_dialog.set_device_configurations(
            previous_device_configurations
        )
        if (
            self.device_configurations_dialog.exec()
            == QtWidgets.QDialog.DialogCode.Accepted
        ):
            new_device_configurations = (
                self.device_configurations_dialog.get_device_configurations()
            )
            with self.session_maker() as session:
                for device_name in session.default_device_configurations:
                    if device_name not in new_device_configurations:
                        del session.default_device_configurations[device_name]
                for (
                    device_name,
                    device_configuration,
                ) in new_device_configurations.items():
                    session.default_device_configurations[device_name] = (
                        device_configuration
                    )

    def closeEvent(self, event):  # noqa: N802
        self.save_window()
        super().closeEvent(event)

    def restore_window(self) -> None:
        ui_settings = QtCore.QSettings()
        state = ui_settings.value(f"{__name__}/state", defaultValue=None)
        if state is not None:
            assert isinstance(state, QtCore.QByteArray)
            self.restoreState(state)
        geometry = ui_settings.value(f"{__name__}/geometry", defaultValue=None)
        if geometry is not None:
            assert isinstance(geometry, QtCore.QByteArray)
            self.restoreGeometry(geometry)

    def save_window(self) -> None:
        ui_settings = QtCore.QSettings()
        ui_settings.setValue(f"{__name__}/state", self.saveState())
        ui_settings.setValue(f"{__name__}/geometry", self.saveGeometry())

    def display_error(self, message: str, exception: TracebackSummary):
        with temporary_widget(ExceptionDialog(self)) as exception_dialog:
            exception_dialog.set_exception(exception)
            exception_dialog.set_message(message)
            exception_dialog.exec()

    def interrupt_sequence(self, path: PureSequencePath):
        experiment_manager = run_with_wip_widget(
            self,
            "Connecting to experiment manager...",
            self.connect_to_experiment_manager,
        )
        # we're actually lying here because we interrupt the running procedure, which
        # may be different from the one passed in argument.
        experiment_manager.interrupt_running_procedure()

    def _on_global_parameters_edited(self, parameters: ParameterNamespace) -> None:
        with self.session_maker() as session:
            session.set_global_parameters(parameters)
            logger.info(f"Global parameters written to storage: {parameters}")

    def signal_exception_while_running_sequence(self, exception: Exception):
        # This is a bit ugly because on_procedure_exception runs a dialog, which
        # messes up the event loop, so instead we schedule the exception handling
        # to be done in the next event loop iteration.
        self.timer.singleShot(
            0, functools.partial(self.on_procedure_exception, exception)
        )

    def _on_about_qt_action_triggered(self):
        QtWidgets.QMessageBox.aboutQt(
            self,
        )

    def _on_about_condetrol_action_triggered(self):
        QtWidgets.QMessageBox.about(
            self,
            "Condetrol",
            "<p><i>Condetrol</i> is a graphical user interface to edit and launch"
            " cold atom experiments.</p>"
            f"<p><i>caqtus-suite</i> version: {__version__}</p>"
            f"<p>Platform: {platform.platform()}</p>",
        )


class BackgroundTask:
    def __init__[
        **P
    ](
        self,
        task: Callable[P, Awaitable[None]],
        sleep_time: float,
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ):
        self.task = task
        self._can_resume: anyio.Event | None = None
        self._cancel_scope: anyio.CancelScope | None = None
        self.sleep_time = sleep_time
        self.args = args
        self.kwargs = kwargs
        self._task_group: anyio.abc.TaskGroup | None = None

    async def run(self) -> Never:
        """Run the background task indefinitely."""

        async with anyio.create_task_group() as self._task_group:
            await self.run_loop()
            await anyio.sleep(math.inf)

    async def run_loop(self) -> None:
        with anyio.CancelScope() as self._cancel_scope:
            while True:
                await self.task(*self.args, **self.kwargs)
                await anyio.sleep(self.sleep_time)

    @contextlib.contextmanager
    def suspend(self):
        """Suspend the background task until the context manager exits.

        When the context manager is entered, the background task is cancelled at the
        next cancellation point.
        When the context manager exits, a new background task is started.
        """

        if self._cancel_scope is None:
            raise RuntimeError("The background task is not running.")
        self._cancel_scope.cancel()
        self._cancel_scope = None

        yield

        assert self._task_group is not None
        self._task_group.start_soon(self.run_loop)

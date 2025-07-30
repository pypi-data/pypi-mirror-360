from __future__ import annotations

import itertools
from typing import Optional

import yaml
from PySide6.QtCore import Qt, QModelIndex, QRect
from PySide6.QtGui import QAction, QFont, QUndoStack, QCursor
from PySide6.QtWidgets import (
    QTableView,
    QMenu,
    QWidget,
    QVBoxLayout,
    QToolBar,
    QDialog,
    QMessageBox,
    QApplication,
)

from caqtus.device import DeviceConfiguration, DeviceName
from caqtus.gui.condetrol._icons import get_icon
from caqtus.gui.qtutil import block_signals, temporary_widget
from caqtus.types.timelane import TimeLanes, TimeLane
from ._delegate import TimeLaneDelegate
from ._time_lanes_model import TimeLanesModel
from .add_lane_dialog import AddLaneDialog
from .extension import CondetrolLaneExtensionProtocol


class TimeLanesEditor(QWidget):
    """A widget for editing the time lanes of a sequence.

    Signals:
        time_lanes_edited: Emitted when the user edits the time lanes.
    """

    def __init__(
        self,
        extension: CondetrolLaneExtensionProtocol,
        device_configurations: dict[DeviceName, DeviceConfiguration],
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.view = TimeLanesView(
            extension=extension,
            device_configurations=device_configurations,
            parent=self,
        )
        self._extension = extension
        self.toolbar = QToolBar(self)
        self.toolbar.setFloatable(False)
        self.toolbar.setMovable(False)
        self.add_lane_action = self.toolbar.addAction(
            get_icon("add-time-lane", self.palette().buttonText().color()), "Add lane"
        )
        self.add_lane_action.triggered.connect(self._on_add_lane_triggered)
        self.simplify_action = self.toolbar.addAction(
            get_icon("simplify-timelanes", self.palette().buttonText().color()),
            "Simplify",
        )
        self.simplify_action.triggered.connect(self._simplify_timelanes)
        self.toolbar.addSeparator()
        self.copy_to_clipboard_action = self.toolbar.addAction(
            get_icon("copy", self.palette().buttonText().color()), "Copy to clipboard"
        )
        self.copy_to_clipboard_action.triggered.connect(self.copy_to_clipboard)
        self.paste_from_clipboard_action = self.toolbar.addAction(
            get_icon("paste", self.palette().buttonText().color()),
            "Paste from clipboard",
        )
        self.paste_from_clipboard_action.triggered.connect(self.paste_from_clipboard)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.view)
        self.setLayout(layout)

        self._add_lane_dialog = AddLaneDialog(self)
        self._add_lane_dialog.set_lane_types(extension.available_new_lanes())

        font = QFont("JetBrains Mono")
        self.setFont(font)

    @property
    def undo_stack(self) -> QUndoStack:
        return self.view.undo_stack

    def set_read_only(self, read_only: bool) -> None:
        """Set the editor to read-only mode.

        In read-only mode, the user cannot edit the time lanes.
        """

        self.view.set_read_only(read_only)

        self.add_lane_action.setEnabled(not read_only)
        self.simplify_action.setEnabled(not read_only)
        self.paste_from_clipboard_action.setEnabled(not read_only)

    def model(self) -> TimeLanesModel:
        return self.view.model()

    def set_time_lanes(self, time_lanes: TimeLanes) -> None:
        """Set the time lanes to be edited.

        The signal time_lanes_edited is not emitted when this method is called.
        """

        with block_signals(self):
            self.model().set_timelanes(time_lanes)

    def get_time_lanes(self) -> TimeLanes:
        """Return a copy of the time lanes currently being edited."""

        return self.model().get_timelanes()

    def has_uncommitted_edits(self) -> bool:
        return self.model().has_uncommitted_edits()

    def commit_edits(self) -> None:
        self.model().commit_edits()

    def _simplify_timelanes(self):
        self.model().simplify()

    def _on_add_lane_triggered(self) -> None:
        if self._add_lane_dialog.exec() == QDialog.DialogCode.Accepted:
            lane_name = self._add_lane_dialog.get_lane_name()
            lane_type = self._add_lane_dialog.get_lane_type()
            if not lane_name:
                return
            if lane_name in self.view.get_time_lanes().lanes:
                QMessageBox.warning(  # type: ignore[reportCallIssue]
                    self,
                    "Lane already exists",
                    f"Can't add the lane <i>{lane_name}</i> because there is already "
                    "a lane with this name.",
                )
            else:
                lane = self._extension.create_new_lane(
                    lane_type, self.view.model().columnCount()
                )
                self.view.add_lane(lane_name, lane)

    def copy_to_clipboard(self):
        time_lanes = self.view.get_time_lanes()
        unstructured = self._extension.unstructure_time_lanes(time_lanes)

        text = yaml.safe_dump(unstructured)
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def paste_from_clipboard(self) -> bool:
        """Paste the content of the clipboard into the editor.

        Returns:
            True if the content was successfully pasted, False otherwise.
        """

        if self.view.is_read_only():
            return False

        clipboard = QApplication.clipboard()
        text = clipboard.text()
        try:
            content = yaml.safe_load(text)
        except yaml.YAMLError as e:
            QMessageBox.warning(  # type: ignore[reportCallIssue]
                self,
                "Invalid YAML content",
                f"Could not parse the clipboard content as YAML:\n {e}",
            )
            return False

        # TODO: raise recoverable error if the content is not valid
        time_lanes = self._extension.structure_time_lanes(content)

        self.model().set_timelanes_with_undo(time_lanes, "paste from clipboard")
        return True


class OverlayStepsView(QTableView):
    def __init__(self, model: TimeLanesModel, parent: TimeLanesView):
        super().__init__(parent)
        self.setModel(model)

        model.rowsInserted.connect(self.hide_lanes)
        model.modelReset.connect(self.hide_lanes)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setSelectionModel(parent.selectionModel())
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.horizontalHeader().hide()
        self.verticalHeader().setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )

        parent.horizontalHeader().sectionResized.connect(self.resize_columns)
        parent.verticalHeader().sectionResized.connect(self.resize_rows)
        self.verticalHeader().sectionResized.connect(self.resize_parent_rows)
        parent.horizontalScrollBar().valueChanged.connect(
            self.horizontalScrollBar().setValue
        )
        self.horizontalScrollBar().valueChanged.connect(
            parent.horizontalScrollBar().setValue
        )

        for column in range(model.columnCount()):
            self.setColumnWidth(column, parent.columnWidth(column))

        self.setRowHeight(0, parent.rowHeight(0))
        self.setRowHeight(1, parent.rowHeight(1))

        self.update_geometry()

        self.verticalScrollBar().valueChanged.connect(
            lambda _: self.verticalScrollBar().setValue(
                self.verticalScrollBar().minimum()
            )
        )
        self.verticalHeader().customContextMenuRequested.connect(
            self._on_steps_context_menu_requested
        )

    def _on_steps_context_menu_requested(self, _):
        if self.is_read_only():
            return

        with temporary_widget(QMenu(self.horizontalHeader())) as menu:
            add_step_action = QAction("Add step")
            menu.addAction(add_step_action)
            add_step_action.triggered.connect(
                lambda: self.model().insertColumn(
                    self.model().columnCount(), QModelIndex()
                )
            )
            menu.exec(QCursor.pos())

    def model(self) -> TimeLanesModel:
        model = super().model()
        assert isinstance(model, TimeLanesModel)
        return model

    def is_read_only(self) -> bool:
        return self.model().is_read_only()

    def parent(self) -> TimeLanesView:
        p = super().parent()
        assert isinstance(p, TimeLanesView)
        return p

    def resize_columns(self, logical_index: int, old_size: int, new_size: int):
        self.setColumnWidth(logical_index, new_size)
        self.update_geometry()

    def resize_parent_rows(self, logical_index: int, old_size: int, new_size: int):
        if logical_index <= 1:
            self.parent().setRowHeight(logical_index, new_size)
            self.update_geometry()

    def resize_rows(self, logical_index: int, old_size: int, new_size: int):
        if logical_index <= 1:
            self.setRowHeight(logical_index, new_size)
            self.update_geometry()

    def hide_lanes(self):
        for row in range(2, self.model().rowCount()):
            self.hideRow(row)

    def update_geometry(self):
        parent = self.parent()
        assert isinstance(parent, TimeLanesView)

        self.setGeometry(
            parent.viewport().x()
            - parent.verticalHeader().width()
            - parent.frameWidth(),
            parent.horizontalHeader().height(),
            parent.width(),
            parent.rowHeight(0) + parent.rowHeight(1) + parent.frameWidth(),
        )


class TimeLanesView(QTableView):
    def __init__(
        self,
        extension: CondetrolLaneExtensionProtocol,
        device_configurations: dict[DeviceName, DeviceConfiguration],
        parent: Optional[QWidget] = None,
    ):
        """A widget for editing time lanes."""

        super().__init__(parent)
        self._model = TimeLanesModel(extension, self)
        self._device_configurations: dict[DeviceName, DeviceConfiguration] = (
            device_configurations
        )
        self._extension = extension
        self.setModel(self._model)

        self.horizontalHeader().setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.verticalHeader().setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setup_connections()

        # self.setSelectionBehavior(QTableView.SelectionBehavior.SelectItems)
        self.setSelectionMode(QTableView.SelectionMode.ContiguousSelection)

        # We disable the auto-scrolling because it is annoying when the view jumps
        # around on its own while the user is trying to edit the time lanes.
        self.setAutoScroll(False)

        self._steps_table = OverlayStepsView(self._model, self)
        self.viewport().stackUnder(self._steps_table)
        self._steps_table.show()
        self.show()
        self._steps_table.update_geometry()
        self.setVerticalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        self.verticalHeader().setFixedWidth(200)
        self._steps_table.verticalHeader().setFixedWidth(200)

    def model(self) -> TimeLanesModel:
        model = super().model()
        assert isinstance(model, TimeLanesModel)
        return model

    @property
    def undo_stack(self) -> QUndoStack:
        return self._model.undo_stack

    def moveCursor(self, cursorAction, modifiers):  # noqa: N802, N803
        current = super().moveCursor(cursorAction, modifiers)

        if cursorAction == QTableView.CursorAction.MoveUp:
            if (current.row() > 1) and (
                self.visualRect(current).topLeft().y()
                < self._steps_table.rowHeight(0) + self._steps_table.rowHeight(1)
            ):
                new_value = (
                    self.verticalScrollBar().value()
                    + self.visualRect(current).topLeft().y()
                    - self._steps_table.rowHeight(0)
                    - self._steps_table.rowHeight(1)
                )
                self.verticalScrollBar().setValue(new_value)
            elif current.row() <= 1:
                return current.siblingAtRow(2)
        return current

    def resizeEvent(self, event):  # noqa: N802
        self._steps_table.update_geometry()
        super().resizeEvent(event)

    def setup_connections(self):
        self.horizontalHeader().customContextMenuRequested.connect(
            self.show_steps_context_menu
        )
        self.verticalHeader().customContextMenuRequested.connect(
            self.show_lanes_context_menu
        )
        self.customContextMenuRequested.connect(self.show_cell_context_menu)

        self._model.dataChanged.connect(self.on_data_changed)
        self._model.rowsInserted.connect(self.on_time_lanes_changed)
        self._model.rowsRemoved.connect(self.on_time_lanes_changed)
        self._model.columnsInserted.connect(self.on_time_lanes_changed)
        self._model.columnsRemoved.connect(self.on_time_lanes_changed)
        self._model.modelReset.connect(self.on_time_lanes_changed)

        # only need to update the lane delegates when the rows change
        self._model.rowsInserted.connect(self.update_delegates)
        self._model.rowsRemoved.connect(self.update_delegates)
        self._model.modelReset.connect(self.update_delegates)

    def on_time_lanes_changed(self):
        self.update_spans()

    def on_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex):
        self.on_time_lanes_changed()

        for row in range(top_left.row(), bottom_right.row() + 1):
            for column in range(top_left.column(), bottom_right.column() + 1):
                index = self._model.index(row, column, QModelIndex())
                span = self._model.span(index)
                if span.width() >= 1 or span.height() >= 1:
                    self.setSpan(row, column, span.height(), span.width())

    def get_time_lanes(self) -> TimeLanes:
        return self._model.get_timelanes()

    def set_time_lanes(self, time_lanes: TimeLanes) -> None:
        self._model.set_timelanes(time_lanes)

    def update_spans(self):
        self.clearSpans()
        for row in range(self._model.rowCount()):
            for column in range(self._model.columnCount()):
                index = self._model.index(row, column, QModelIndex())
                span = self._model.span(index)
                if span.width() >= 1 or span.height() >= 1:
                    self.setSpan(row, column, span.height(), span.width())

    def update_delegates(self):
        for row in range(self._model.rowCount()):
            previous_delegate = self.itemDelegateForRow(row)
            if previous_delegate:
                previous_delegate.deleteLater()
            self.setItemDelegateForRow(row, None)  # type: ignore[reportArgumentType]
        for row in range(2, self._model.rowCount()):
            lane = self._model.get_lane(row - 2)
            name = self._model.get_lane_name(row - 2)
            delegate = self._construct_delegate(lane, name)
            self.setItemDelegateForRow(row, delegate)  # type: ignore[reportArgumentType]
            if delegate:
                delegate.setParent(self)

    def _construct_delegate(
        self, lane: TimeLane, lane_name: str
    ) -> Optional[TimeLaneDelegate]:
        delegate = self._extension.get_lane_delegate(lane, lane_name)
        if delegate is not None:
            if not isinstance(delegate, TimeLaneDelegate):
                raise TypeError(
                    f"Invalid delegate type: {type(delegate)}. "
                    "The delegate must be an instance of TimeLaneDelegate."
                )
            delegate.setParent(self)
            delegate.set_device_configurations(self._device_configurations)
            delegate.set_parameter_names(set())
        return delegate

    def set_read_only(self, read_only: bool) -> None:
        self._model.set_read_only(read_only)

    def is_read_only(self) -> bool:
        return self._model.is_read_only()

    def show_steps_context_menu(self, pos):
        if self.is_read_only():
            return
        menu = QMenu(self.horizontalHeader())

        index = self.horizontalHeader().logicalIndexAt(pos.x())
        if index == -1:
            add_step_action = QAction("Add step")
            menu.addAction(add_step_action)
            add_step_action.triggered.connect(
                lambda: self._model.insertColumn(
                    self._model.columnCount(), QModelIndex()
                )
            )
        elif 0 <= index < self.model().columnCount():
            add_step_before_action = QAction("Insert step before")
            menu.addAction(add_step_before_action)
            add_step_before_action.triggered.connect(
                lambda: self._model.insertColumn(index, QModelIndex())
            )

            add_step_after_action = QAction("Insert step after")
            menu.addAction(add_step_after_action)
            add_step_after_action.triggered.connect(
                lambda: self._model.insertColumn(index + 1, QModelIndex())
            )
            if self.model().columnCount() > 1:
                remove_step_action = QAction("Remove")
                menu.addAction(remove_step_action)
                remove_step_action.triggered.connect(
                    lambda: self._model.removeColumn(index, QModelIndex())
                )
        menu.exec(self.horizontalHeader().mapToGlobal(pos))
        menu.deleteLater()

    def show_lanes_context_menu(self, pos):
        if self.is_read_only():
            return
        menu = QMenu(self.verticalHeader())

        index = self.verticalHeader().logicalIndexAt(pos.y())
        if 2 <= index < self.model().rowCount():
            remove_lane_action = QAction("Remove")
            menu.addAction(remove_lane_action)
            remove_lane_action.triggered.connect(
                lambda: self._model.remove_lane(index - 2)
            )
            for action in self._model.get_lane_header_context_actions(index - 2):
                if isinstance(action, QAction):
                    menu.addAction(action)
                elif isinstance(action, QMenu):
                    menu.addMenu(action)
        else:
            return
        menu.exec(self.verticalHeader().mapToGlobal(pos))
        menu.deleteLater()

    def show_cell_context_menu(self, pos):
        if self.is_read_only():
            return
        index = self.indexAt(pos)
        cell_actions = self._model.get_cell_context_actions(index)
        selection = self.selectionModel().selection()

        with temporary_widget(QMenu(self)) as menu:
            if selection.contains(index):
                merge_action = menu.addAction(f"Expand step {index.column()}")
                merge_action.triggered.connect(
                    lambda: self.expand_step(index.column(), selection)
                )

            for action in cell_actions:
                if isinstance(action, QAction):
                    menu.addAction(action)
                elif isinstance(action, QMenu):
                    menu.addMenu(action)
            menu.exec(self.viewport().mapToGlobal(pos))

    def expand_step(self, step: int, selection):
        indices: set[tuple[int, int]] = set()
        for selection_range in selection:
            top_left = selection_range.topLeft()
            bottom_right = selection_range.bottomRight()
            indices.update(
                itertools.product(
                    range(top_left.row(), bottom_right.row() + 1),
                    range(top_left.column(), bottom_right.column() + 1),
                )
            )

        for row, group in itertools.groupby(sorted(indices), key=lambda x: x[0]):
            group = list(group)
            start = group[0][1]
            stop = group[-1][1]
            self._model.expand_step(step, row - 2, start, stop)

    def add_lane(self, lane_name: str, lane: TimeLane):
        self._model.insert_time_lane(lane_name, lane)

    def visualRect(self, index):  # noqa: N802
        rect = super().visualRect(index)
        if not isinstance(rect, QRect):
            # Not sure this case can actually happen, maybe rect can be None?
            return rect

        # Here we make sure that the rect is within the viewport horizontally.
        # This is useful because when a delegate creates an editor widget, it uses
        # the visualRect method to position the editor.
        # We want the editor to always be fully visible in the viewport, even if the
        # cell is only partially visible.
        viewport_rect = self.viewport().rect()
        if rect.left() < viewport_rect.left():
            rect.setLeft(viewport_rect.left())
        if rect.right() > viewport_rect.right():
            rect.setRight(viewport_rect.right())
        return rect

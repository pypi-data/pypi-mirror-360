import functools
from collections.abc import Set
from typing import Optional

import yaml
from PySide6 import QtWidgets
from PySide6.QtCore import Qt, QPersistentModelIndex, QModelIndex
from PySide6.QtGui import (
    QKeySequence,
    QShortcut,
    QFont,
    QGuiApplication,
    QUndoStack,
)
from PySide6.QtWidgets import QWidget, QTreeView, QAbstractItemView, QMenu

from caqtus.gui.qtutil._temporary_widget import temporary_widget
from caqtus.types.expression import Expression
from caqtus.types.iteration import (
    StepsConfiguration,
    VariableDeclaration,
    ExecuteShot,
    LinspaceLoop,
    ArangeLoop,
)
from caqtus.types.variable_name import DottedVariableName
from caqtus.utils import serialization
from .delegate import StepDelegate
from .steps_model import StepsModel
from ..sequence_iteration_editor import SequenceIterationEditor
from ..._icons import get_icon


def create_shot_step() -> ExecuteShot:
    return ExecuteShot()


def create_variable_declaration():
    return VariableDeclaration(
        variable=DottedVariableName("new_variable"), value=Expression("...")
    )


def create_linspace_loop():
    return LinspaceLoop(
        variable=DottedVariableName("new_variable"),
        start=Expression("..."),
        stop=Expression("..."),
        num=10,
        sub_steps=[],
    )


def create_arange_loop():
    return ArangeLoop(
        variable=DottedVariableName("new_variable"),
        start=Expression("..."),
        stop=Expression("..."),
        step=Expression("..."),
        sub_steps=[],
    )


class StepsIterationEditor(QTreeView, SequenceIterationEditor[StepsConfiguration]):
    """Editor for the steps of a sequence.

    .. figure:: screenshot_StepsIterationEditor.png
       :align: center

       Example of a StepsIterationEditor.

    Args:
        parent: The parent widget of the editor.

    Signals:
        iteration_edited: Emitted when the iteration displayed by the editor is changed
            by the user.
            This signal is not emitted when the iteration is set programmatically.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._model = StepsModel(StepsConfiguration([]))
        self.setModel(self._model)
        self.expandAll()
        self.header().hide()
        self._delegate = StepDelegate(self)
        self.setItemDelegate(self._delegate)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)

        self.delete_shortcut = QShortcut(QKeySequence("Delete"), self)
        self.delete_shortcut.activated.connect(self.delete_selected)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.select_all_shortcut = QShortcut(QKeySequence("Ctrl+A"), self)
        self.select_all_shortcut.activated.connect(self.selectAll)
        self.copy_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        self.copy_shortcut.activated.connect(self.copy_selection)
        self.cut_shortcut = QShortcut(QKeySequence("Ctrl+X"), self)
        self.cut_shortcut.activated.connect(self.cut_selected)
        self.paste_shortcut = QShortcut(QKeySequence("Ctrl+V"), self)
        self.paste_shortcut.activated.connect(self.paste)

        font = QFont("JetBrains Mono")
        font.setPixelSize(13)
        self.setFont(font)

        self.toolbar = QtWidgets.QToolBar()
        self.add_button = QtWidgets.QToolButton(self)
        self.add_menu = QMenu(self)
        self.add_shot_action = self.add_menu.addAction("shot")
        self.add_variable_action = self.add_menu.addAction("variable")
        self.add_linspace_action = self.add_menu.addAction("linspace loop")
        self.add_arange_action = self.add_menu.addAction("arange loop")
        self._setup_add_button()
        self.toolbar.addWidget(self.add_button)

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

    def has_uncommitted_edits(self) -> bool:
        return not self.undo_stack.isClean()

    def commit_edits(self) -> None:
        self.undo_stack.setClean()

    @property
    def undo_stack(self) -> QUndoStack:
        """The undo stack used by the editor.

        This undo stack is used to undo and redo the changes made by the user in the
        editor.
        """

        return self._model.undo_stack

    def _setup_add_button(self):
        self.add_button.setToolTip("Add step")
        self.add_button.setPopupMode(
            QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup
        )
        self.add_button.setIcon(get_icon("plus", self.palette().buttonText().color()))
        self.add_button.setMenu(self.add_menu)
        self.add_shot_action.triggered.connect(
            functools.partial(
                self._model.insert_steps,
                [create_shot_step()],
                self._model.rowCount(),
                QModelIndex(),
            )
        )
        self.add_variable_action.triggered.connect(
            functools.partial(
                self._model.insert_steps,
                [create_variable_declaration()],
                0,
                QModelIndex(),
            )
        )
        self.add_linspace_action.triggered.connect(
            functools.partial(
                self._model.insert_steps, [create_linspace_loop()], 0, QModelIndex()
            )
        )
        self.add_arange_action.triggered.connect(
            functools.partial(
                self._model.insert_steps, [create_arange_loop()], 0, QModelIndex()
            )
        )

    def get_iteration(self) -> StepsConfiguration:
        """Returns the iteration currently displayed by the editor.

        This method returns a copy of the iteration, so the caller can modify it
        without affecting the editor.
        """

        return self._model.get_steps()

    def set_iteration(self, iteration: StepsConfiguration):
        """Updates the iteration displayed by the editor.

        This method does not emit the signal iteration_edited.
        """

        self._model.set_steps(iteration)
        self.expandAll()

    def set_available_parameter_names(self, parameter_names: Set[DottedVariableName]):
        """Sets the names that can be used in the iteration.

        The names are used to populate the auto-completion of variable names when the
        user try to edit the name of a variable or a loop.
        """

        self._delegate.set_available_names(parameter_names)

    def set_read_only(self, read_only: bool) -> None:
        """Sets the editor in read-only mode.

        When the editor is in read-only mode, the user cannot edit the steps.

        Even if the editor is in read-only mode, the iteration can still be set
        programmatically with :meth:`set_iteration`.
        """

        self._model.set_read_only(read_only)
        self.paste_from_clipboard_action.setEnabled(not read_only)
        self.add_button.setEnabled(not read_only)

    def is_read_only(self) -> bool:
        """Returns whether the editor is in read-only mode."""

        return self._model.is_read_only()

    def delete_selected(self) -> bool:
        if self.is_read_only():
            return False
        self._model.remove_indices(self.selectedIndexes())
        return True

    def copy_selection(self) -> None:
        selected_indexes = self.selectedIndexes()
        data = self._model.mimeData(selected_indexes)
        clipboard = QGuiApplication.clipboard()
        clipboard.setMimeData(data)

    def cut_selected(self) -> bool:
        if self.is_read_only():
            return False

        self.copy_selection()
        self._model.remove_indices(self.selectedIndexes())
        return True

    def paste(self) -> bool:
        if self.is_read_only():
            return False

        clipboard = QGuiApplication.clipboard()
        data = clipboard.mimeData()

        if self.selectedIndexes():
            first = QPersistentModelIndex(self.selectedIndexes()[0])
            parent = first.parent()
            row = first.row()
            if self._model.dropMimeData(data, Qt.DropAction.MoveAction, row, 0, parent):
                self._model.removeRow(first.row(), first.parent())
        else:
            parent = QModelIndex()
            row = self._model.rowCount()
            self._model.dropMimeData(data, Qt.DropAction.MoveAction, row, 0, parent)
        return True

    def show_context_menu(self, position):
        index = self.indexAt(position)
        if not index.isValid():
            return
        with temporary_widget(QMenu(self)) as menu:
            add_menu = menu.addMenu("Insert above...")

            create_variable_action = add_menu.addAction("variable")
            new_variable = create_variable_declaration()
            create_variable_action.triggered.connect(
                functools.partial(
                    self._model.insert_steps,
                    [new_variable],
                    index.row(),
                    index.parent(),
                )
            )
            create_shot_action = add_menu.addAction("Shot")
            new_shot = ExecuteShot()
            create_shot_action.triggered.connect(
                functools.partial(
                    self._model.insert_steps, [new_shot], index.row(), index.parent()
                )
            )
            create_linspace_action = add_menu.addAction("Linspace loop")
            new_linspace = create_linspace_loop()
            create_linspace_action.triggered.connect(
                functools.partial(
                    self._model.insert_steps,
                    [new_linspace],
                    index.row(),
                    index.parent(),
                )
            )
            create_arange_action = add_menu.addAction("Arange loop")
            new_arange = create_arange_loop()
            create_arange_action.triggered.connect(
                functools.partial(
                    self._model.insert_steps, [new_arange], index.row(), index.parent()
                )
            )
            menu.exec(self.mapToGlobal(position))

    def copy_to_clipboard(self):
        steps = self.get_iteration()

        unstructured = serialization.converters["json"].unstructure(
            steps, StepsConfiguration
        )

        text = yaml.safe_dump(unstructured)
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)

    def paste_from_clipboard(self) -> bool:
        """Attempts to paste the content of the clipboard.

        If the editor is in read-only mode, this method does nothing.
        """

        if self._model.is_read_only():
            return False

        clipboard = QGuiApplication.clipboard()
        text = clipboard.text()
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as e:
            QtWidgets.QMessageBox.warning(  # type: ignore[reportCallIssue]
                self,
                "Invalid YAML content",
                f"Could not parse the clipboard content as YAML:\n {e}",
            )
            return False

        # TODO: raise recoverable exception if data is not valid
        config = serialization.structure(data, StepsConfiguration)
        self._model.replace_steps(config.steps, "paste from clipboard")

        return True

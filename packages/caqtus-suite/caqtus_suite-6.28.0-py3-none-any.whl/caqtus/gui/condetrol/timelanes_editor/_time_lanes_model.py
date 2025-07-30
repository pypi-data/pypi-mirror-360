from __future__ import annotations

import functools
from typing import Optional

import attrs
from PySide6.QtCore import (
    QAbstractTableModel,
    QObject,
    QModelIndex,
    Qt,
    QSize,
    QPersistentModelIndex,
)
from PySide6.QtGui import QAction, QUndoStack, QUndoCommand
from PySide6.QtWidgets import QMenu

from caqtus.types.expression import Expression
from caqtus.types.timelane import TimeLanes, TimeLane
from ._time_lane_model import TimeLaneModel
from ._time_step_model import (
    TimeStepNameModel,
    TimeStepDurationModel,
)
from .extension import CondetrolLaneExtensionProtocol

_DEFAULT_MODEL_INDEX = QModelIndex()


class TimeLanesModel(QAbstractTableModel):
    """Table model for time lanes of a sequence.

    Each column represents a step in the shot.
    The first row contains the names of the steps.
    The second row contains the durations of the steps.
    The following rows contain the lanes of the sequence.

    This model has an undo stack when actions are performed.
    """

    # Ignore some lint rules for this class as PySide6 models have a lot of camelCase
    # methods.
    # ruff: noqa: N802
    def __init__(
        self,
        extension: CondetrolLaneExtensionProtocol,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self.undo_stack = QUndoStack()
        self.undo_stack.setClean()
        self._step_names_model = TimeStepNameModel(self.undo_stack, self)
        self._step_durations_model = TimeStepDurationModel(self.undo_stack, self)
        self._lane_models: list[TimeLaneModel] = []
        self._extension = extension

        self._step_names_model.dataChanged.connect(self._on_step_names_data_changed)
        self._step_durations_model.dataChanged.connect(
            self._on_step_durations_data_changed
        )
        self._read_only = False

    def set_read_only(self, read_only: bool) -> None:
        self._read_only = read_only

    def is_read_only(self) -> bool:
        return self._read_only

    def has_uncommitted_edits(self) -> bool:
        """Indicate if the user has edited data since calling :meth:`commit_edits`.

        This value is orthogonal to :meth:`is_read_only` as the model can be read only
        and still have uncommitted edits.
        """

        return not self.undo_stack.isClean()

    def commit_edits(self) -> None:
        """Marks the model has having no uncommitted edits.

        Typically, one would call this method after saving the result of
        :meth:`get_timelanes`.
        """

        self.undo_stack.setClean()

    def get_timelanes(self) -> TimeLanes:
        """Return a copy of the lanes currently in the model."""

        return TimeLanes(
            step_names=self._step_names_model.get_names(),
            step_durations=self._step_durations_model.get_duration(),
            lanes={
                get_lane_model_name(model): model.get_lane()
                for model in self._lane_models
            },
        )

    def cell_index(self, lane_index: int, step: int) -> QModelIndex:

        return self.index(lane_index + 2, step)

    def _on_step_names_data_changed(
        self,
        top_left: QModelIndex,
        bottom_right: QModelIndex,
        roles: list[Qt.ItemDataRole],
    ):
        self.dataChanged.emit(
            self.index(0, top_left.row()), self.index(0, bottom_right.row())
        )

    def _on_step_durations_data_changed(
        self,
        top_left: QModelIndex,
        bottom_right: QModelIndex,
        roles: list[Qt.ItemDataRole],
    ):
        self.dataChanged.emit(
            self.index(1, top_left.row()), self.index(1, bottom_right.row())
        )

    def set_timelanes(self, timelanes: TimeLanes):
        """Set the lanes of the model.

        Calling this method clears the undo stack of the model.
        """

        # Don't check if read only, because we need to update the content of the editor
        # even if it is readonly when swapping sequences.
        new_models = []
        for name, lane in timelanes.lanes.items():
            lane_model = self._create_lane_model(name, lane)
            new_models.append(lane_model)

        self.beginResetModel()
        self.undo_stack.clear()
        self._step_names_model.set_names(timelanes.step_names)
        self._step_durations_model.set_durations(timelanes.step_durations)
        self._lane_models.clear()
        self._lane_models.extend(new_models)
        self.endResetModel()

    def set_timelanes_with_undo(self, timelanes: TimeLanes, message: str) -> bool:
        if self._read_only:
            return False
        new_models = []
        for name, lane in timelanes.lanes.items():
            lane_model = self._create_lane_model(name, lane)
            new_models.append(lane_model)
        self.undo_stack.push(
            self._SetTimeLanesCommand(
                self,
                list(self._lane_models),
                list(new_models),
                self._step_names_model.get_names(),
                list(timelanes.step_names),
                list(self._step_durations_model.get_duration()),
                list(timelanes.step_durations),
                message,
            )
        )
        return True

    @attrs.define(slots=False)
    class _SetTimeLanesCommand(QUndoCommand):
        model: TimeLanesModel
        old_models: list[TimeLaneModel]
        new_models: list[TimeLaneModel]
        old_names: list[str]
        new_names: list[str]
        old_durations: list[Expression]
        new_durations: list[Expression]
        message: str

        def __attrs_post_init__(self):
            super().__init__(self.message)

        def redo(self):
            self.model.beginResetModel()
            self.model._step_names_model.set_names(self.new_names)
            self.model._step_durations_model.set_durations(self.new_durations)
            self.model._lane_models.clear()
            self.model._lane_models.extend(self.new_models)
            self.model.endResetModel()

        def undo(self):
            self.model.beginResetModel()
            self.model._step_names_model.set_names(self.old_names)
            self.model._step_durations_model.set_durations(self.old_durations)
            self.model._lane_models.clear()
            self.model._lane_models.extend(self.old_models)
            self.model.endResetModel()

    def _create_lane_model(self, name: str, lane: TimeLane) -> TimeLaneModel:
        lane_model = self._extension.get_lane_model(lane, name)
        lane_model.setParent(self)
        lane_model.set_lane(lane)
        lane_model.set_undo_stack(self.undo_stack)
        lane_model.dataChanged.connect(
            # For some reason, functools.partial does not work here, but lambda does.
            # functools.partial(
            #     self.on_lane_model_data_changed, lane_model=lane_model
            # )
            lambda top_left, bottom_right: self._on_lane_model_data_changed(
                top_left, bottom_right, lane_model
            )
        )
        lane_model.modelReset.connect(
            functools.partial(self._on_lane_model_reset, lane_model=lane_model)
        )
        lane_model.headerDataChanged.connect(
            functools.partial(self._on_lane_header_data_changed, lane_model=lane_model)
        )
        return lane_model

    def _on_lane_model_reset(self, lane_model: TimeLaneModel):
        lane_index = self._lane_models.index(lane_model)
        self.dataChanged.emit(
            self.index(lane_index + 2, 0),
            self.index(lane_index + 2, self.columnCount() - 1),
        )

    def _on_lane_model_data_changed(
        self,
        top_left: QModelIndex,
        bottom_right: QModelIndex,
        lane_model: TimeLaneModel,
    ):
        lane_index = self._lane_models.index(lane_model)
        self.dataChanged.emit(
            self.index(lane_index + 2, top_left.row()),
            self.index(lane_index + 2, bottom_right.row()),
        )

    def _on_lane_header_data_changed(
        self,
        orientation: Qt.Orientation,
        first: int,
        last: int,
        lane_model: TimeLaneModel,
    ):
        lane_index = self._lane_models.index(lane_model)
        if orientation == Qt.Orientation.Horizontal:
            self.headerDataChanged.emit(
                Qt.Orientation.Vertical,
                lane_index + 2,
                lane_index + 2,
            )

    def get_lane(self, index: int) -> TimeLane:
        return self._lane_models[index].get_lane()

    def get_lane_name(self, index: int) -> str:
        return get_lane_model_name(self._lane_models[index])

    def number_steps(self) -> int:
        count = self._step_names_model.rowCount()
        assert count == self._step_durations_model.rowCount()
        return count

    def get_step_name(self, step: int) -> str:
        name = self._step_names_model.data(
            self._step_names_model.index(step), Qt.ItemDataRole.DisplayRole
        )
        assert isinstance(name, str)
        return name

    def columnCount(
        self, parent: QModelIndex | QPersistentModelIndex = _DEFAULT_MODEL_INDEX
    ) -> int:
        return self.number_steps()

    def rowCount(
        self, parent: QModelIndex | QPersistentModelIndex = _DEFAULT_MODEL_INDEX
    ) -> int:
        return len(self._lane_models) + 2

    def data(self, index, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        return self._map_to_source(index).data(role)

    def setData(self, index, value, role: int = Qt.ItemDataRole.EditRole) -> bool:
        if self._read_only:
            return False
        if not index.isValid():
            return False
        if role != Qt.ItemDataRole.EditRole:
            return False
        if index.row() == 0:
            return self._step_names_model.setData(
                self._step_names_model.index(index.column()), value
            )
        elif index.row() == 1:
            return self._step_durations_model.setData(
                self._step_durations_model.index(index.column()), value
            )
        else:
            return self._lane_models[index.row() - 2].setData(
                self._map_to_source(index), value
            )

    def _set_data(self, value, row: int, column: int) -> None:
        index = self.index(row, column)
        mapped_index = self._map_to_source(index)
        result = mapped_index.model().setData(
            mapped_index, value, Qt.ItemDataRole.EditRole
        )
        assert result

    class _SetValueCommand(QUndoCommand):
        def __init__(self, model: TimeLanesModel, new_value, row: int, column: int):
            self.previous_value = model.data(
                model.index(row, column), Qt.ItemDataRole.EditRole
            )
            if row == 0:
                msg = (
                    f"change step {column} name from <{self.previous_value}> to "
                    f"<{new_value}>"
                )
            elif row == 1:
                msg = (
                    f"change step {column} duration from <{self.previous_value}> to "
                    f"<{new_value}>"
                )
            else:
                msg = (
                    f"change value of lane {model.get_lane_name(row-2)} from "
                    f"<{self.previous_value}> to <{new_value}> for step {column}"
                )

            super().__init__(msg)
            self.model = model
            self.new_value = new_value
            self.row = row
            self.column = column

        def redo(self) -> None:
            self.model._set_data(self.new_value, self.row, self.column)

        def undo(self) -> None:
            self.model._set_data(self.previous_value, self.row, self.column)

    def flags(self, index) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        mapped_index = self._map_to_source(index)
        flags = mapped_index.model().flags(mapped_index)
        if self._read_only:
            flags &= ~Qt.ItemFlag.ItemIsEditable
            flags &= ~Qt.ItemFlag.ItemIsDropEnabled
        return flags

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ):
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return f"Step {section}"
        elif orientation == Qt.Orientation.Vertical:
            if section == 0:
                return self._step_names_model.headerData(
                    0, Qt.Orientation.Horizontal, role
                )
            elif section == 1:
                return self._step_durations_model.headerData(
                    0, Qt.Orientation.Horizontal, role
                )
            else:
                return self._lane_models[section - 2].headerData(
                    0, Qt.Orientation.Horizontal, role
                )

    def insertColumn(
        self,
        column: int,
        parent: QModelIndex | QPersistentModelIndex = _DEFAULT_MODEL_INDEX,
    ) -> bool:
        """Add a new time step at the requested column.

        If performed, pushes the action on the model undo stack.

        Returns:
            False if no action was performed if the model is read only or if the column
            index is not valid.
            True otherwise if the action was performed.
        """

        if self._read_only:
            return False
        if not (0 <= column <= self.columnCount()):
            return False
        self.undo_stack.beginMacro(f"insert step {column}")
        self.undo_stack.push(self._BeginInsertColumnCommand(self, column))
        self._step_names_model.insertRow(column)
        self._step_durations_model.insertRow(column)
        for model in self._lane_models:
            model.insertRow(column)
        self.undo_stack.push(self._EndInsertColumnCommand(self, column))
        self.undo_stack.endMacro()
        return True

    @attrs.frozen(slots=False)
    class _BeginInsertColumnCommand(QUndoCommand):
        model: TimeLanesModel
        column: int

        def __attrs_post_init__(self):
            super().__init__(f"begin insert column {self.column}")

        def redo(self) -> None:
            assert not self.model._read_only

            self.model.beginInsertColumns(QModelIndex(), self.column, self.column)

        def undo(self) -> None:
            assert not self.model._read_only
            self.model.endRemoveColumns()

    @attrs.frozen(slots=False)
    class _EndInsertColumnCommand(QUndoCommand):
        model: TimeLanesModel
        column: int

        def __attrs_post_init__(self):
            super().__init__("end insert column {self.column}")

        def redo(self) -> None:
            assert not self.model._read_only
            self.model.endInsertColumns()

        def undo(self) -> None:
            assert not self.model._read_only
            self.model.beginRemoveColumns(QModelIndex(), self.column, self.column)

    def removeColumn(
        self, column, parent: QModelIndex | QPersistentModelIndex = _DEFAULT_MODEL_INDEX
    ) -> bool:
        """Remove a step from the model.

        If an action was performed, pushes the action on the model undo stack.

        Returns:
            False if no action was performed if the model is read only or if the column
            index is not valid.
            True otherwise.
        """

        if self._read_only:
            return False
        if not (0 <= column < self.columnCount()):
            return False
        self.undo_stack.beginMacro(f"remove step {column}")
        self.undo_stack.push(self._BeginRemoveColumnCommand(self, column))
        self._step_names_model.removeRow(column)
        self._step_durations_model.removeRow(column)
        for lane_model in self._lane_models:
            lane_model.removeRow(column)
        self.undo_stack.push(self._EndRemoveColumnCommand(self, column))
        self.undo_stack.endMacro()
        return True

    @attrs.frozen(slots=False)
    class _BeginRemoveColumnCommand(QUndoCommand):
        model: TimeLanesModel
        column: int

        def __attrs_post_init__(self):
            super().__init__(f"begin remove column {self.column}")

        def redo(self) -> None:
            assert not self.model._read_only
            self.model.beginRemoveColumns(QModelIndex(), self.column, self.column)

        def undo(self) -> None:
            assert not self.model._read_only
            self.model.endInsertColumns()

    @attrs.frozen(slots=False)
    class _EndRemoveColumnCommand(QUndoCommand):
        model: TimeLanesModel
        column: int

        def __attrs_post_init__(self):
            super().__init__(f"end remove column {self.column}")

        def redo(self) -> None:
            assert not self.model._read_only
            self.model.endRemoveColumns()

        def undo(self) -> None:
            assert not self.model._read_only
            self.model.beginInsertColumns(QModelIndex(), self.column, self.column)

    def lane_number(self) -> int:
        return len(self._lane_models)

    def lane_names(self) -> set[str]:
        """Return the names of the lanes contained in the model."""

        return set(
            model.headerData(0, Qt.Orientation.Horizontal)
            for model in self._lane_models
        )

    def insert_time_lane(
        self, name: str, time_lane: TimeLane, index: Optional[int] = None
    ) -> bool:
        if self._read_only:
            return False
        if index is None:
            index = len(self._lane_models)
        if not (0 <= index <= len(self._lane_models)):
            raise IndexError(f"Index {index} is out of range")
        if len(time_lane) != self.columnCount():
            raise ValueError(
                f"Length of time lane ({len(time_lane)}) does not match "
                f"number of columns ({self.columnCount()})"
            )

        if name in self.lane_names():
            raise ValueError(f"Name {name} is already used")
        lane_model = self._create_lane_model(name, time_lane)
        self.undo_stack.push(self._InsertTimeLaneCommand(self, index, lane_model))
        return True

    @attrs.define(slots=False)
    class _InsertTimeLaneCommand(QUndoCommand):
        model: TimeLanesModel
        index: int
        time_lane_model: TimeLaneModel

        def __attrs_post_init__(self):
            super().__init__(f"insert lane {self.time_lane_model.name()}")

        def redo(self):
            self.model._insert_lane_model(self.index, self.time_lane_model)

        def undo(self):
            self.model._pop_lane_model(self.index)

    def _insert_lane_model(self, index: int, lane_model: TimeLaneModel) -> None:
        assert 0 <= index <= self.lane_number()
        self.beginInsertRows(QModelIndex(), index + 2, index + 2)
        self._lane_models.insert(index, lane_model)
        self.endInsertRows()

    def remove_lane(self, lane_index: int) -> bool:
        """Remove a lane from the model.

        This method replaces :meth:`removeRow` as not all rows can be removed.
        Push the action on the model undo stack.
        """

        if self._read_only:
            return False
        if not (0 <= lane_index < self.lane_number()):
            return False
        self.undo_stack.push(self._RemoveTimeLaneCommand(self, lane_index))
        return True

    class _RemoveTimeLaneCommand(QUndoCommand):
        def __init__(self, model: "TimeLanesModel", index: int):
            self.name = model.get_lane_name(index)
            super().__init__(f"remove lane {self.name}")
            self.model = model
            self.index = index
            self.time_lane_model: TimeLaneModel | None = None

        def redo(self):
            self.time_lane_model = self.model._pop_lane_model(self.index)

        def undo(self):
            assert self.time_lane_model is not None
            self.model._insert_lane_model(self.index, self.time_lane_model)
            self.time_lane_model = None

    def _pop_lane_model(self, lane_index: int) -> TimeLaneModel:
        assert 0 <= lane_index < len(self._lane_models)
        self.beginRemoveRows(QModelIndex(), lane_index + 2, lane_index + 2)
        model = self._lane_models.pop(lane_index)
        self.endRemoveRows()
        return model

    def get_cell_context_actions(self, index: QModelIndex) -> list[QAction | QMenu]:
        if not index.isValid():
            return []
        if self._read_only:
            return []
        if index.row() >= 2:
            return self._lane_models[index.row() - 2].get_cell_context_actions(
                self._map_to_source(index)
            )
        else:
            return []

    def get_lane_header_context_actions(self, lane_index: int) -> list[QAction | QMenu]:
        if not 0 <= lane_index < len(self._lane_models):
            return []
        if self._read_only:
            return []
        return self._lane_models[lane_index].get_header_context_actions()

    def span(self, index):
        if not index.isValid():
            return QSize(1, 1)
        if index.row() >= 2:
            mapped_index = self._map_to_source(index)
            span = self._lane_models[index.row() - 2].span(mapped_index)
            return QSize(span.height(), span.width())
        return QSize(1, 1)

    def expand_step(self, step: int, lane_index: int, start: int, stop: int) -> bool:
        if self._read_only:
            return False
        if not (0 <= step < self.columnCount()):
            return False
        if not (0 <= lane_index < self.lane_number()):
            return False
        lane_model = self._lane_models[lane_index]
        return lane_model.expand_step(step, start, stop)

    def _map_to_source(self, index: QModelIndex | QPersistentModelIndex) -> QModelIndex:
        assert index.isValid()
        assert self.hasIndex(index.row(), index.column())
        if index.row() == 0:
            return self._step_names_model.index(index.column(), 0)
        elif index.row() == 1:
            return self._step_durations_model.index(index.column(), 0)
        else:
            return self._lane_models[index.row() - 2].index(index.column(), 0)

    def simplify(self) -> bool:
        if self._read_only:
            return False
        self.undo_stack.beginMacro("simplify")
        for lane_model in self._lane_models:
            lane_model.simplify()
        self.undo_stack.endMacro()
        return True


def get_lane_model_name(model: TimeLaneModel) -> str:
    lane_name = model.headerData(
        0, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole
    )
    if not isinstance(lane_name, str):
        raise TypeError(f"Expected str, got {type(lane_name)}")
    return lane_name

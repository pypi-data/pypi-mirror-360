from __future__ import annotations

from abc import abstractmethod
from typing import Optional, TypeVar, Generic, Callable, NewType

import attrs
from PySide6.QtWidgets import QWidget

import caqtus.gui.qtutil.qabc as qabc
from caqtus.session._shot_id import ShotId
from caqtus.utils.serialization import JSON


class ShotView(QWidget, metaclass=qabc.QABCMeta):
    @abstractmethod
    async def display_shot(self, shot: ShotId) -> None:
        raise NotImplementedError


S = TypeVar("S", bound=JSON)
V = TypeVar("V", bound=ShotView)

ManagerName = NewType("ManagerName", str)


@attrs.define
class ViewManager(Generic[V, S]):
    constructor: Callable[[S], V]
    dumper: Callable[[V], S]
    state_generator: Callable[[QWidget], Optional[tuple[str, S]]]

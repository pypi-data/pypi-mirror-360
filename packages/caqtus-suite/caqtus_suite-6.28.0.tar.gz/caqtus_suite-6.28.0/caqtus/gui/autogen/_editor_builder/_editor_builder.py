import enum
import typing
from collections.abc import Callable

import attrs

from .._value_editor import ValueEditor

# TODO: Use PEP 747 if accepted
type TypeExpr[T] = typing.Any

type EditorFactory[T] = Callable[[], ValueEditor[T]]
"""A function that can be used to create an editor for a value."""


class EditorBuilder:
    """Construct widgets to edit values of given types.

    Editors must be registered with the builder using the method :meth:`register_editor`
    before the method :meth:`build_editor` is called.
    """

    def __init__(self) -> None:
        self._editor_factories: dict[TypeExpr, EditorFactory] = {}

    def register_editor[T](self, type_: TypeExpr[T], factory: EditorFactory) -> None:
        """Specify an editor to use when encountering a given type.

        When the method :meth:`build_editor` is called with this type, this editor
        will be used.

        Warning:
            If an editor is already registered for this type, it will be overwritten.
        """

        self._editor_factories[type_] = factory

    def build_editor(self, type_: TypeExpr) -> EditorFactory:
        """Construct a gui class to edit value of a given type.

        This method dispatches the type passed as argument to the editor registered
        for this type.

        If the type is `typing.Annotated[T, ...]`, the editor for `T` will be built.

        If the type is not registered, but is an attrs class, an editor will be built
        for it by calling :func:`build_attrs_class_editor`.

        If the type is not registered but is a `typing.Literal`, an editor will be built
        for it by calling :func:`build_literal_editor`.

        Raises:
            TypeNotRegisteredError: If no editor is registered to handle the given type,
                and it is not possible to infer an editor from the type.
        """

        origin = typing.get_origin(type_)

        if origin is typing.Annotated:  # typing.Annotated[T, ...]
            try:
                return self.build_editor(typing.get_args(type_)[0])
            except Exception as e:
                e.add_note(f"The error occurred while processing the type {type_}")
                raise e from e.__cause__

        try:
            return self._editor_factories[type_]
        except KeyError:
            if origin == typing.Literal:
                from ._literal import build_literal_editor

                return build_literal_editor(*typing.get_args(type_))
            elif issubclass(type_, enum.Enum):
                from ._enum import EnumEditor, generate_enum_editor

                return generate_enum_editor(type_)
            elif attrs.has(type_):
                from ._attrs import build_attrs_class_editor

                return build_attrs_class_editor(type_, self)
            else:
                raise TypeNotRegisteredError(
                    f"No editor is registered to handle {type_}"
                ) from None


class EditorBuildingError(Exception):
    pass


class TypeNotRegisteredError(EditorBuildingError):
    pass

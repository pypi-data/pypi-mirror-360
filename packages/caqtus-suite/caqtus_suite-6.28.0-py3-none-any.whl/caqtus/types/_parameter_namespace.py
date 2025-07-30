from collections.abc import Mapping
from typing import Optional, Generic, TypeVar

from benedict import benedict  # type: ignore

from caqtus.types.variable_name import DottedVariableName

T = TypeVar("T")


class VariableNamespace(Generic[T]):
    def __init__(self, initial_variables: Optional[dict] = None):
        if initial_variables is not None:
            # noinspection PyProtectedMember
            self._dict = benedict(initial_variables)
        else:
            self._dict: benedict = benedict()

    def update(self, values: dict[DottedVariableName, T]):
        for key, value in values.items():
            self._dict[str(key)] = value

    def to_flat_dict(self) -> dict[DottedVariableName, T]:
        return {
            DottedVariableName(name.replace("$", ".")): value
            for name, value in self._dict.flatten(separator="$").items()
        }

    def __getitem__(self, item: DottedVariableName) -> T:
        return self._dict[str(item)]  # type: ignore[reportReturnType]

    def __contains__(self, item: DottedVariableName) -> bool:
        return str(item) in self._dict

    def __or__(
        self, other: Mapping[DottedVariableName, T]
    ) -> dict[DottedVariableName, T]:
        if isinstance(other, Mapping):
            new = self._dict.clone()
            for key, value in other.items():
                new[key] = value  # type: ignore[reportArgumentType]
            return new  # type: ignore[no-any-return]
        else:
            return NotImplemented

    def __repr__(self):
        return f"{self.__class__.__name__}({self._dict})"

    def dict(self):
        return self._dict

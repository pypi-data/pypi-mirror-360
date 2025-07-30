import abc
import bisect
import itertools
from collections.abc import MutableSequence, Iterable, Sequence, Iterator
from typing import TypeVar, Self, NewType, overload, Never

import attrs
from typing_extensions import deprecated

from caqtus.types.expression import Expression
from caqtus.utils.asserts import assert_length_changed

#: Represents the index of a single step in a time lane.
Step = NewType("Step", int)

#: Represents the index of a block of steps in a time lane.
Block = NewType("Block", int)

#: Represents the number of steps spanned by a block.
Span = NewType("Span", int)


@attrs.define(init=False, eq=False, repr=False)
class TimeLane[T](MutableSequence[T], abc.ABC):
    """Represents a sequence of values covering some steps in time.

    A time lane is a sequence of values that are associated with some time steps.
    The time steps are not explicitly stored in the lane.
    Instead, for a given lane, lane[i] is the value of the lane at the i-th step.

    Consecutive identical values in a lane can be grouped in a single block spanning
    multiple steps.

    TimeLane is an abstract class, generic over the type of values it contains.
    It provides common methods such as value access, insertion, and deletion.
    """

    # spanned_values[i] is the value of i-th block of the lane and the number of steps
    # it spans.
    _spanned_values: list[tuple[T, Span]] = attrs.field()

    # _bounds[i] is the step at which the i-th block starts (inclusive)
    # _bounds[i+1] is the step at which the i-th block ends (exclusive)
    _bounds: list[Step] = attrs.field(init=False, repr=False)

    @_spanned_values.validator  # type: ignore
    def validate_spanned_values(self, _, value):
        if not all(span >= 1 for _, span in value):
            raise ValueError("Span must be at least 1")

    def __init__(self, values: Iterable[T]):
        """Initialize the lane with the given values.

        This constructor will group consecutive values that share the same id into
        blocks.

        This means that the following three lanes have the same blocks with length 3, 2,
        and 1:
        DigitalTimeLane([(True, 3), (False, 2), (True, 1)])
        DigitalTimeLane([True, True, True, False, False, True])
        DigitalTimeLane([True] * 3 + [False] * 2 + [True])

        Note however that the two following lanes are equivalent:
        AnalogTimeLane([Expression("...")] * 2 + [Expression("...")] * 3)
        AnalogTimeLane([(Expression("..."), 2), (Expression("..."), 3)])
        but are different from:
        AnalogTimeLane([Expression("...")] * 5)

        """

        values_list = list(values)
        spanned_values = []
        for _, group in itertools.groupby(values_list, key=id):
            g = list(group)
            spanned_values.append((g[0], Span(len(g))))
        self._spanned_values = spanned_values
        self._bounds = compute_bounds(span for _, span in self._spanned_values)

    @classmethod
    def from_spanned_values(cls, spanned_values: Iterable[tuple[T, Span]]) -> Self:
        obj = cls.__new__(cls)
        obj._spanned_values = list(spanned_values)
        obj._bounds = compute_bounds(span for _, span in obj._spanned_values)
        return obj

    def spanned_values(self) -> Sequence[tuple[T, Span]]:
        """Returns the spanned values of the lane.

        For each block in the lane, returns a tuple of two elements: the value of the
        block and the number of steps spanned by the block.

        Examples:
            >>> from caqtus.types.timelane import DigitalTimeLane
            >>> lane = DigitalTimeLane([True, True, False, True])
            >>> lane.spanned_values()
            [(True, 2), (False, 1), (True, 1)]
        """

        return tuple(self._spanned_values)

    @property
    def number_blocks(self) -> int:
        """Returns the number of blocks in the lane."""

        return len(self._spanned_values)

    def get_bounds(self, step: Step) -> tuple[Step, Step]:
        """Returns the bounds of the block containing the given step."""

        step = self._normalize_step(step)
        if not (0 <= step < len(self)):
            raise IndexError(f"Index out of bounds: {step}")
        return self.get_block_bounds(find_containing_block(self._bounds, step))

    def block_values(self) -> Iterator[T]:
        """Returns an iterator over the block values.

        The length of the iterator is the number of blocks in the lane, not the number
        of steps.
        """

        return (value for value, _ in self._spanned_values)

    @deprecated("use block_values instead")
    def values(self) -> Iterator[T]:
        return self.block_values()

    def block_bounds(self) -> Iterator[tuple[Step, Step]]:
        """Iterates over the bounds of the blocks.

        Returns:
            An iterator over the bounds of the blocks.

            Its elements are tuples of two elements: the step (inclusive) at which the
            block starts and the step (exclusive) at which the block ends.

            The length of the iterator is the number of blocks in the lane.
        """

        return zip(self._bounds[:-1], self._bounds[1:], strict=True)

    def get_block_bounds(self, block: Block) -> tuple[Step, Step]:
        """Returns the bounds of the given block.

        Returns:
            A tuple of two elements: the step (inclusive) at which the block starts and
            the step (exclusive) at which the block ends.

        Raises:
            IndexError: If the block index is out of bounds.
        """

        if not (0 <= block < self.number_blocks):
            raise IndexError(f"Block index out of bounds: {block}")

        return self._bounds[block], self._bounds[block + 1]

    @deprecated("use block_bounds instead")
    def bounds(self) -> Iterator[tuple[Step, Step]]:
        return self.block_bounds()

    def _get_containing_block(self, index: Step) -> Block:
        return find_containing_block(self._bounds, index)

    def _get_block_span(self, block: Block) -> Span:
        return self._spanned_values[block][1]

    def get_block_value(self, block: Block) -> T:
        """Returns the value of the given block."""

        return self._spanned_values[block][0]

    def __len__(self):
        return self._bounds[-1]

    @overload
    def __getitem__(self, item: int) -> T: ...

    @overload
    def __getitem__(self, item: slice) -> Never: ...

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._get_value_at_step(Step(item))
        else:
            raise TypeError(f"Invalid type for item: {type(item)}")

    def _get_value_at_step(self, step: Step) -> T:
        step = self._normalize_step(step)
        if not (0 <= step < len(self)):
            raise IndexError(f"Step out of bounds: {step}")
        return self.get_block_value(find_containing_block(self._bounds, step))

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.set_value_at_step(Step(key), value)
        elif isinstance(key, slice):
            self.set_value_for_slice(key, value)
        else:
            raise TypeError(f"Invalid type for item: {type(key)}")

    def set_value_at_step(self, step: Step, value: T):
        step = self._normalize_step(step)
        if not (0 <= step < len(self)):
            raise IndexError(f"Step out of bounds: {step}")
        block = find_containing_block(self._bounds, step)
        start, stop = self.get_block_bounds(block)
        before_length = Span(step - start)
        after_length = Span(stop - step - 1)
        previous_value = self.get_block_value(block)
        insert_index = block
        if before_length > 0:
            self._spanned_values.insert(insert_index, (previous_value, before_length))
            insert_index += 1
        self._spanned_values[insert_index] = (value, Span(1))
        insert_index += 1
        if after_length > 0:
            self._spanned_values.insert(insert_index, (previous_value, after_length))
        self._bounds = compute_bounds(span for _, span in self._spanned_values)

    def set_value_for_slice(self, slice_: slice, value: T):
        start = self._normalize_step(
            Step(slice_.start if slice_.start is not None else 0)
        )
        stop = self._normalize_step(
            Step(slice_.stop if slice_.stop is not None else len(self))
        )
        if not (0 <= start <= stop <= len(self)):
            raise IndexError(f"Slice out of bounds: {slice_}")
        if slice_.step is not None:
            raise ValueError(f"Slice step must be None: {slice_}")
        before_block = find_containing_block(self._bounds, start)
        before_length = Span(start - self.get_block_bounds(before_block)[0])
        before_value = self.get_block_value(before_block)
        if stop == len(self):
            after_block = Block(len(self._spanned_values) - 1)
        else:
            after_block = find_containing_block(self._bounds, stop)
        after_length = Span(self.get_block_bounds(after_block)[1] - stop)
        after_value = self.get_block_value(after_block)
        del self._spanned_values[before_block : after_block + 1]
        insert_index = before_block
        if before_length > 0:
            self._spanned_values.insert(before_block, (before_value, before_length))
            insert_index += 1
        self._spanned_values.insert(insert_index, (value, Span(stop - start)))
        insert_index += 1
        if after_length > 0:
            self._spanned_values.insert(insert_index, (after_value, after_length))
        self._bounds = compute_bounds(span for _, span in self._spanned_values)

    def _normalize_step(self, step: Step) -> Step:
        if step < 0:
            step = Step(len(self) + step)
        return step

    def __delitem__(self, key):
        if isinstance(key, int):
            self.delete_step(Step(key))
        else:
            raise TypeError(f"Invalid type for item: {type(key)}")

    def delete_step(self, step: Step) -> None:
        """Delete a single step from the lane.

        The length of the lane is always exactly one less after this operation.
        """

        previous_length = len(self)

        step = self._normalize_step(step)
        if not (0 <= step < len(self)):
            raise IndexError(f"Index out of bounds: {step}")
        block = find_containing_block(self._bounds, step)
        if self._get_block_span(block) == 1:
            del self._spanned_values[block]
        else:
            self._spanned_values[block] = (
                self.get_block_value(block),
                Span(self._get_block_span(block) - 1),
            )
        self._bounds = compute_bounds(span for _, span in self._spanned_values)
        assert len(self) == previous_length - 1

    @assert_length_changed(+1)
    def insert(self, index: int, value: T) -> None:
        step = Step(index)
        step = self._normalize_step(step)
        if step == len(self):
            self._spanned_values.append((value, Span(1)))
            self._bounds.append(Step(self._bounds[-1] + 1))
            return
        if not (0 <= step < len(self)):
            raise IndexError(f"Step out of bounds: {step}")
        block = find_containing_block(self._bounds, step)
        start, stop = self.get_block_bounds(block)
        before_length = Span(step - start)
        after_length = Span(stop - step)
        previous_value = self.get_block_value(block)
        insert_index = block
        if before_length > 0:
            self._spanned_values.insert(insert_index, (previous_value, before_length))
            insert_index += 1
        self._spanned_values[insert_index] = (value, Span(1))
        insert_index += 1
        if after_length > 0:
            self._spanned_values.insert(insert_index, (previous_value, after_length))
        self._bounds = compute_bounds(span for _, span in self._spanned_values)

    def __repr__(self):
        to_concatenate = []
        for length, group in itertools.groupby(
            self._spanned_values, key=lambda x: x[1]
        ):
            if length == 1:
                to_concatenate.append(
                    f"[{', '.join(repr(value) for value, _ in group)}]"
                )
            else:
                to_concatenate.extend(
                    [f"[{repr(value)}] * {length}" for value, _ in group]
                )
        formatted = " + ".join(to_concatenate)
        return f"{type(self).__name__}({formatted})"

    def __eq__(self, other):
        if isinstance(other, TimeLane):
            return self._spanned_values == other._spanned_values
        elif isinstance(other, Sequence):
            if len(self) != len(other):
                return False
            return all(a == b for a, b in zip(self, other, strict=True))
        else:
            return NotImplemented


TimeLaneType = TypeVar("TimeLaneType", bound=TimeLane)


def compute_bounds(spans: Iterable[Span]) -> list[Step]:
    return [0] + list(itertools.accumulate(spans))  # type: ignore


def find_containing_block(bounds: Sequence[Step], index: Step) -> Block:
    return Block(bisect.bisect(bounds, index) - 1)


@attrs.define(eq=False)
class TimeLanes:
    """A collection of time lanes.

    Groups together multiple time lanes and the associated step names and durations.
    """

    step_names: list[str] = attrs.field(
        factory=list,
        validator=attrs.validators.deep_iterable(
            iterable_validator=attrs.validators.instance_of(list),
            member_validator=attrs.validators.instance_of(str),
        ),
        on_setattr=attrs.setters.validate,
    )
    step_durations: list[Expression] = attrs.field(
        factory=list,
        validator=attrs.validators.deep_iterable(
            iterable_validator=attrs.validators.instance_of(list),
            member_validator=attrs.validators.instance_of(Expression),
        ),
        on_setattr=attrs.setters.validate,
    )
    lanes: dict[str, TimeLane] = attrs.field(
        factory=dict,
        validator=attrs.validators.deep_mapping(
            key_validator=attrs.validators.instance_of(str),
            value_validator=attrs.validators.instance_of(TimeLane),
        ),
        on_setattr=attrs.setters.validate,
    )

    @classmethod
    def empty(cls) -> Self:
        return cls([], [], {})

    @step_names.validator  # type: ignore
    def validate_step_names(self, _, value):
        if not all(isinstance(v, str) for v in value):
            raise ValueError("All step names must be instances of str")

    @step_durations.validator  # type: ignore
    def validate_step_durations(self, _, value):
        if len(value) != len(self.step_names):
            raise ValueError(
                "The number of step durations must match the number of step names"
            )
        if not all(isinstance(v, Expression) for v in value):
            raise ValueError("All step durations must be instances of Expression")

    @lanes.validator  # type: ignore
    def validate_lanes(self, _, value):
        if not all(isinstance(v, TimeLane) for v in value.values()):
            raise ValueError("All lanes must be instances of TimeLane")
        for name, lane in value.items():
            if len(lane) != self.number_steps:
                raise ValueError(
                    f"Lane '{name}' does not have the same length as the time steps"
                )

    @property
    def number_steps(self) -> int:
        """The number of steps in the time lanes.

        The number of steps is the same as the length of each lane.
        """

        return len(self.step_names)

    @property
    def number_lanes(self) -> int:
        """Returns the number of lanes."""

        return len(self.lanes)

    def __setitem__(self, name: str, lane: TimeLane):
        """Sets the value of a lane.

        Raises:
            TypeError: If the lane value is not an instance of TimeLane.
            TypeError: If the lane name is not a string.
            ValueError: If the lane value has a different length than the other lanes.
        """

        if not isinstance(lane, TimeLane):
            raise TypeError(f"Invalid type for value: {type(lane)}")
        if not isinstance(name, str):
            raise TypeError(f"Invalid type for key: {type(name)}")
        if len(lane) != self.number_steps:
            raise ValueError("All lanes must have the same length")

        self.lanes[name] = lane

    def __getitem__(self, key: str) -> TimeLane:
        """Returns the value of a lane.

        Raises:
            KeyError: If the lane name is not found.
        """

        return self.lanes[key]

    def __eq__(self, other):
        if not isinstance(other, TimeLanes):
            return NotImplemented
        return (
            self.step_names == other.step_names
            and self.step_durations == other.step_durations
            and self.lanes == other.lanes
            # We say that two TimeLanes are different if the order of the lanes is
            # different.
            # This is because the order of the lanes is important for the user.
            and list(self.lanes.keys()) == list(other.lanes.keys())
        )

from __future__ import annotations

import collections
from collections.abc import Sequence, Mapping
from typing import assert_never, Optional, Any, assert_type

import attrs
import numpy as np
import numpy.typing as npt

import caqtus.formatter as fmt
from caqtus.device.output_transform import evaluate
from caqtus.types.expression import Expression
from caqtus.types.parameter import Parameters
from caqtus.types.recoverable_exceptions import InvalidValueError, InvalidTypeError
from caqtus.types.timelane import AnalogTimeLane, Ramp, Block
from caqtus.types.units import (
    ureg,
    Quantity,
    dimensionless,
    InvalidDimensionalityError,
    Unit,
    is_scalar_quantity,
)
from caqtus.types.units.base import is_in_base_units, BaseUnit
from caqtus.types.variable_name import VariableName, DottedVariableName
from ..timed_instructions import (
    TimedInstruction,
    Pattern,
    concatenate,
    create_ramp,
)
from ..timing import Time, number_ticks, start_tick, stop_tick

TIME_VARIABLE = VariableName("t")


@attrs.frozen
class DimensionedSeries[T: (np.number, np.bool_)]:
    """Represents a series of value to output on a channel with their units.

    Parameters:
        values: The sequence of values to output.
        units: The units in which the values are expressed.
            They must be in base SI units.
    """

    values: TimedInstruction[T]
    units: BaseUnit = attrs.field()

    @units.validator  # type: ignore[reportAttributeAccessIssue]
    def _validate_units(self, _, units):
        if not isinstance(units, Unit):
            raise TypeError(f"Expected a unit, got {type(units)}")
        if not is_in_base_units(units):
            raise ValueError(
                f"Unit {units} is not expressed in the base units of the registry."
            )


def compile_analog_lane(
    lane: AnalogTimeLane,
    variables: Parameters,
    step_start_times: Sequence[Time],
    time_step: Time,
) -> DimensionedSeries[np.float64]:
    """Compile the lane to a sequencer instruction.

    This function discretizes the lane time and evaluates the expressions and ramps
    in the lane for each tick.

    Args:
        lane: The lane to compile.
        variables: The values of the variables to use when evaluating the expressions
            in the lane.
        step_start_times: The start times in seconds of each step.
            This must have one more element than the number of steps in the lane, with
            the last element being the total duration of the shot.
        time_step: The time step in seconds to use for the discretization.

    Returns:
        The computed instruction for the lane.
        This contains an instruction with the values for each tick, and the unit in
        which they are expressed.
    """

    if len(lane) + 1 != len(step_start_times):
        raise ValueError(
            f"Number of steps in lane ({len(lane)}) does not match number of"
            f" step start times ({len(step_start_times)})"
        )

    # We do a first pass to compile the blocks that contain expressions, and we ignore
    # the blocks that contain ramps.
    # This is necessary because ramps need to know the value of the surrounding blocks
    # to be computed.
    expression_results: dict[Block, ConstantBlockResult | TimeDependentBlockResult] = {}
    for block_index, block_value in enumerate(lane.block_values()):
        block_start_step, block_stop_step = lane.get_block_bounds(Block(block_index))
        block_start_time = step_start_times[block_start_step]
        block_stop_time = step_start_times[block_stop_step]
        if isinstance(block_value, Expression):
            expr_result = _compile_expression_block(
                block_value,
                variables,
                block_start_time,
                block_stop_time,
                time_step,
            )
            expression_results[Block(block_index)] = expr_result
        elif isinstance(block_value, Ramp):
            continue
        else:
            assert_never(block_value)

    if len(expression_results) == 0:
        raise InvalidValueError("Lane must contain at least one expression block")

    unique_units = get_unique_units(
        {block: result.unit for block, result in expression_results.items()}
    )
    assert len(unique_units) > 0

    if len(unique_units) > 1:
        error = InvalidDimensionalityError(
            "All expressions in the lane must evaluate to the same unit"
        )
        for unit, blocks in unique_units.items():
            error.add_note(
                f"Block group {tuple(blocks)} evaluate to "
                f"{fmt.unit(unit or dimensionless)}"
            )
        raise error

    ramp_results: dict[Block, RampBlockResult] = {}
    for block_index, block_value in enumerate(lane.block_values()):
        if isinstance(block_value, Ramp):
            ramp_result = _compile_ramp_cell(
                lane,
                Block(block_index),
                expression_results,
                step_start_times,
                time_step,
            )
            ramp_results[Block(block_index)] = ramp_result
        elif isinstance(block_value, Expression):
            continue
        else:
            assert_never(block_value)

    block_results = expression_results | ramp_results

    assert len(block_results) == lane.number_blocks
    # Need to ensure that the instructions are sorted by block index before
    # concatenating
    instructions = (
        block_results[Block(block)].to_instruction()
        for block in range(lane.number_blocks)
    )
    total_instruction = concatenate(*instructions)

    units = {result.unit for result in block_results.values()}
    assert len(units) == 1
    unit = next(iter(units))

    return DimensionedSeries(total_instruction, unit)


def get_unique_units(
    units: Mapping[Block, Optional[Unit]]
) -> dict[Optional[Unit], list[Block]]:
    unique_units = collections.defaultdict(list)

    for block, unit in units.items():
        unique_units[unit].append(block)

    return unique_units


def _compile_expression_block(
    expression: Expression,
    variables: Mapping[DottedVariableName, Any],
    start_time: Time,
    stop_time: Time,
    time_step: Time,
) -> ConstantBlockResult | TimeDependentBlockResult:
    if is_constant(expression):
        length = number_ticks(start_time, stop_time, time_step)
        return evaluate_constant_expression(expression, variables, length)
    else:
        return evaluate_time_dependent_expression(
            expression, variables, start_time, stop_time, time_step
        )


def evaluate_constant_expression(
    expression: Expression,
    variables: Mapping[DottedVariableName, Any],
    length: int,
) -> ConstantBlockResult:
    value = evaluate(expression, variables)

    if is_scalar_quantity(value):
        return ConstantBlockResult(
            value=value.magnitude,
            length=length,
            unit=value.units,
        )
    else:
        assert_type(value, float | int | bool)
        return ConstantBlockResult(
            value=float(value),
            length=length,
            unit=dimensionless,
        )


def evaluate_time_dependent_expression(
    expression: Expression,
    variables: Mapping[DottedVariableName, Any],
    start_time: Time,
    stop_time: Time,
    time_step: Time,
) -> TimeDependentBlockResult:
    assert not is_constant(expression)

    time_values = get_time_array(start_time, stop_time, time_step) - float(start_time)
    # The first time is not necessarily 0, it is the time of the first tick of the
    # block.
    # Same for the last time which is not necessarily stop_time - start_time, but the
    # time of the last tick of the block.
    # If a ramp precedes this block, we also want to know the value of the current block
    # at true t=0, so we compute this as well.
    # Same if a ramp follows this block, we want to know the value of the current block
    # at true t=stop_time - start_time.
    time_values = np.insert(
        time_values, [0, len(time_values)], [0, float(stop_time - start_time)]
    )

    t = time_values * ureg.s
    variables = dict(variables) | {TIME_VARIABLE: t}
    evaluated = expression.evaluate(variables)

    if isinstance(evaluated, Quantity):
        in_base_units = evaluated.to_base_units()
        magnitudes = in_base_units.magnitude
        if not isinstance(magnitudes, np.ndarray):
            raise InvalidTypeError(
                f"{fmt.expression(expression)} does not evaluate to a series of values"
            )
        unit = in_base_units.units
    elif isinstance(evaluated, np.ndarray):
        magnitudes = evaluated
        unit = dimensionless
    else:
        raise InvalidTypeError(
            f"{fmt.expression(expression)} does not evaluate to a series of values"
        )
    length = number_ticks(start_time, stop_time, time_step)
    if magnitudes.shape != (length + 2,):
        raise InvalidValueError(
            f"{fmt.expression(expression)} evaluates to an array of shape"
            f" {magnitudes.shape} while a shape of {(length,)} is expected",
        )
    return TimeDependentBlockResult(
        values=magnitudes[1:-1].astype(np.float64),
        unit=unit,
        initial_value=float(magnitudes[0]),
        final_value=float(magnitudes[-1]),
    )


def _compile_ramp_cell(
    lane: AnalogTimeLane,
    ramp_block: Block,
    expression_blocks: dict[Block, ConstantBlockResult | TimeDependentBlockResult],
    step_bounds: Sequence[Time],
    time_step: Time,
) -> RampBlockResult:
    previous_block = Block(ramp_block - 1)
    if previous_block < 0:
        raise InvalidValueError("There can't be a ramp at the beginning of a lane")
    next_block = Block(ramp_block + 1)
    if next_block >= lane.number_blocks:
        raise InvalidValueError("There can't be a ramp at the end of a lane")

    try:
        previous_block_result = expression_blocks[previous_block]
    except KeyError:
        raise InvalidValueError(
            f"Block {previous_block} that precedes a ramp must be an expression"
        ) from None
    try:
        next_block_result = expression_blocks[next_block]
    except KeyError:
        raise InvalidValueError(
            f"Block {next_block} that follows a ramp must be an expression"
        ) from None

    assert previous_block_result.unit == next_block_result.unit

    ramp_start_value = previous_block_result.get_final_value()
    ramp_end_value = next_block_result.get_initial_value()

    ramp_start_step, ramp_end_step = lane.get_block_bounds(ramp_block)

    ramp_start_time = step_bounds[ramp_start_step]
    ramp_end_time = step_bounds[ramp_end_step]

    return RampBlockResult.through_two_points(
        ramp_start_time,
        ramp_start_value,
        ramp_end_time,
        ramp_end_value,
        time_step,
        previous_block_result.unit,
    )


def is_constant(expression: Expression) -> bool:
    return TIME_VARIABLE not in expression.upstream_variables


def get_time_array(
    start: Time, stop: Time, time_step: Time
) -> np.ndarray[Any, np.dtype[np.floating]]:
    times = np.arange(
        start_tick(start, time_step),
        stop_tick(stop, time_step),
        dtype=np.float64,
    ) * float(time_step)
    return times


@attrs.frozen
class ConstantBlockResult:
    """Result of compiling a constant block."""

    value: float
    length: int
    unit: BaseUnit

    def get_initial_value(self) -> float:
        return self.value

    def get_final_value(self) -> float:
        return self.value

    def to_instruction(self) -> TimedInstruction[np.float64]:
        return Pattern([self.value]) * self.length


@attrs.frozen(eq=False)
class TimeDependentBlockResult:
    """Result of compiling a time-dependent block."""

    values: npt.NDArray[np.float64]
    unit: BaseUnit

    initial_value: float
    final_value: float

    def __eq__(self, other):
        if not isinstance(other, TimeDependentBlockResult):
            return NotImplemented
        return (
            np.allclose(self.values, other.values)
            and self.unit == other.unit
            and self.initial_value == other.initial_value
            and self.final_value == other.final_value
        )

    def get_initial_value(self) -> float:
        return self.initial_value

    def get_final_value(self) -> float:
        return self.final_value

    def to_instruction(self) -> TimedInstruction[np.float64]:
        return Pattern(self.values, dtype=np.dtype(np.float64))


@attrs.frozen
class RampBlockResult:
    """Result of compiling a ramp block."""

    initial_value: float
    final_value: float
    length: int

    unit: BaseUnit

    @classmethod
    def through_two_points(
        cls,
        t0: Time,
        v0: float,
        t1: Time,
        v1: float,
        time_step: Time,
        unit: BaseUnit,
    ) -> RampBlockResult:
        def f(t: Time) -> float:
            return float((t - t0) / (t1 - t0)) * (v1 - v0) + v0

        first_tick = start_tick(t0, time_step)
        last_tick = stop_tick(t1, time_step)

        first_tick_time = Time(first_tick * time_step)
        last_tick_time = Time(last_tick * time_step)

        length = last_tick - first_tick

        if length == 0:
            # We can pick whatever value we want, as the ramp has no length.
            # However, we need to be careful to not call f with t0 == t1 as this will
            # raise a ZeroDivisionError.
            initial_value = v0
            final_value = v1
        else:
            initial_value = f(first_tick_time)
            final_value = f(last_tick_time)

        return RampBlockResult(
            initial_value,
            final_value,
            length,
            unit,
        )

    def to_instruction(self) -> TimedInstruction[np.float64]:
        return create_ramp(self.initial_value, self.final_value, self.length)

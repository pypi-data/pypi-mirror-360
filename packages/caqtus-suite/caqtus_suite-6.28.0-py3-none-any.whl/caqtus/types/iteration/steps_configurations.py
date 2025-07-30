from __future__ import annotations

import functools
from collections.abc import Iterable, Callable, Generator
from collections.abc import Mapping, Iterator
from typing import TypeAlias, TypeGuard, Any, assert_type, override, assert_never, Self

import attrs
import numpy

import caqtus.formatter as fmt
from caqtus.types.expression import Expression
from caqtus.types.parameter import (
    NotAnalogValueError,
    Parameter,
    ParameterSchema,
)
from caqtus.types.parameter import is_parameter
from caqtus.types.recoverable_exceptions import InvalidTypeError
from caqtus.utils import serialization
from ._step_context import StepContext
from .iteration_configuration import IterationConfiguration, Unknown
from ..parameter._analog_value import is_scalar_analog_value, ScalarAnalogValue
from ..recoverable_exceptions import EvaluationError
from ..units import (
    DimensionalityError,
    InvalidDimensionalityError,
    dimensionless,
    Quantity,
    Unit,
)
from ..variable_name import DottedVariableName


def validate_step(instance, attribute, step):
    if is_step(step):
        return
    else:
        raise TypeError(f"Invalid step: {step}")


@attrs.define
class ContainsSubSteps:
    sub_steps: list[Step] = attrs.field(
        validator=attrs.validators.deep_iterable(
            iterable_validator=attrs.validators.instance_of(list),
            member_validator=validate_step,
        ),
        on_setattr=attrs.setters.validate,
    )


@attrs.define
class VariableDeclaration:
    """Represents the declaration of a variable.

    Attributes:
        variable: The name of the variable.
        value: The unevaluated to assign to the variable.
    """

    __match_args__ = ("variable", "value")

    variable: DottedVariableName = attrs.field(
        validator=attrs.validators.instance_of(DottedVariableName),
        on_setattr=attrs.setters.validate,
    )
    value: Expression = attrs.field(
        validator=attrs.validators.instance_of(Expression),
        on_setattr=attrs.setters.validate,
    )

    def __str__(self):
        return f"{self.variable} = {self.value}"


@attrs.define
class LinspaceLoop(ContainsSubSteps):
    """Represents a loop that iterates between two values with a fixed number of steps.

    Attributes:
        variable: The name of the variable that is being iterated over.
        start: The start value of the variable.
        stop: The stop value of the variable.
        num: The number of steps to take between the start and stop values.
    """

    __match_args__ = (
        "variable",  # pyright: ignore[reportAssignmentType]
        "start",
        "stop",
        "num",
        "sub_steps",
    )
    variable: DottedVariableName = attrs.field(
        validator=attrs.validators.instance_of(DottedVariableName),
        on_setattr=attrs.setters.validate,
    )
    start: Expression = attrs.field(
        validator=attrs.validators.instance_of(Expression),
        on_setattr=attrs.setters.validate,
    )
    stop: Expression = attrs.field(
        validator=attrs.validators.instance_of(Expression),
        on_setattr=attrs.setters.validate,
    )
    num: int = attrs.field(
        converter=int,
        validator=attrs.validators.ge(0),
        on_setattr=attrs.setters.pipe(attrs.setters.convert, attrs.setters.validate),
    )

    def __str__(self):
        return f"linspace loop over {self.variable}"

    def loop_values(
        self, evaluation_context: Mapping[DottedVariableName, Any]
    ) -> Iterator[ScalarAnalogValue]:
        """Returns the values that the variable represented by this loop takes.

        Args:
            evaluation_context: Contains the value of the variables with which to
                evaluate the start and stop expressions of the loop.

        Raises:
            EvaluationError: if the start or stop expressions could not be evaluated.
            NotAnalogValueError: if the start or stop expressions don't evaluate to an
                analog value.
            DimensionalityError: if the start or stop values are not commensurate.
        """

        try:
            start = _to_scalar_analog_value(self.start.evaluate(evaluation_context))
        except NotAnalogValueError:
            raise NotAnalogValueError(
                f"Start {fmt.expression(self.start)} of {self} does not evaluate to an "
                f"analog value"
            ) from None
        try:
            stop = _to_scalar_analog_value(self.stop.evaluate(evaluation_context))
        except NotAnalogValueError:
            raise NotAnalogValueError(
                f"Stop {fmt.expression(self.stop)} of {self} does not evaluate to an "
                f"analog value"
            ) from None

        # Here we enforce that the values generated have the same format as the start
        # value.
        if isinstance(start, float):
            try:
                stop = _to_dimensionless_float(stop)
            except DimensionalityError:
                raise InvalidDimensionalityError(
                    f"Start {fmt.expression(self.start)} of {self} is "
                    f"dimensionless, but stop {fmt.expression(self.stop)} cannot "
                    f"be converted to dimensionless"
                ) from None
            assert_type(stop, float)
            assert_type(start, float)
            for value in numpy.linspace(start, stop, self.num):
                yield float(value.item())
        elif isinstance(start, int):
            raise AssertionError("start must be strictly a float or a Quantity")
        else:
            try:
                stop = _to_unit(stop, start.units)
            except DimensionalityError as e:
                raise InvalidDimensionalityError(
                    f"Start {fmt.expression(self.start)} of {self} has invalid "
                    f"dimensionality."
                ) from e
            assert_type(start, Quantity[float])
            assert_type(stop, Quantity[float])
            for value in numpy.linspace(start.magnitude, stop.magnitude, self.num):
                yield Quantity(float(value), start.units)


@attrs.define
class ArangeLoop(ContainsSubSteps):
    """Represents a loop that iterates between two values with a fixed step size.

    Attributes:
        variable: The name of the variable that is being iterated over.
        start: The start value of the variable.
        stop: The stop value of the variable.
        step: The step size between each value.
    """

    __match_args__ = (
        "variable",  # pyright: ignore[reportAssignmentType]
        "start",
        "stop",
        "step",
        "sub_steps",
    )
    variable: DottedVariableName = attrs.field(
        validator=attrs.validators.instance_of(DottedVariableName),
        on_setattr=attrs.setters.validate,
    )
    start: Expression = attrs.field(
        validator=attrs.validators.instance_of(Expression),
        on_setattr=attrs.setters.validate,
    )
    stop: Expression = attrs.field(
        validator=attrs.validators.instance_of(Expression),
        on_setattr=attrs.setters.validate,
    )
    step: Expression = attrs.field(
        validator=attrs.validators.instance_of(Expression),
        on_setattr=attrs.setters.validate,
    )

    def __str__(self):
        return f"arange loop over {fmt.shot_param(self.variable)}"

    def loop_values(
        self, evaluation_context: Mapping[DottedVariableName, Any]
    ) -> Iterator[ScalarAnalogValue]:
        """Returns the values that the variable represented by this loop takes.

        Args:
            evaluation_context: Contains the value of the variables with which to
                evaluate the start, stop and step expressions of the loop.

        Raises:
            EvaluationError: if the start, stop or step expressions could not be
                evaluated.
            NotAnalogValueError: if the start, stop or step expressions don't evaluate
                to an analog value.
            InvalidDimensionalityError: if the start, stop and step values are not
                commensurate.
        """

        try:
            start = _to_scalar_analog_value(self.start.evaluate(evaluation_context))
        except NotAnalogValueError:
            raise NotAnalogValueError(
                f"Start {fmt.expression(self.start)} of {self} does not evaluate to an "
                f"analog value"
            ) from None
        try:
            stop = _to_scalar_analog_value(self.stop.evaluate(evaluation_context))
        except NotAnalogValueError:
            raise NotAnalogValueError(
                f"Stop {fmt.expression(self.stop)} of {self} does not evaluate to an "
                f"analog value"
            ) from None
        try:
            step = _to_scalar_analog_value(self.step.evaluate(evaluation_context))
        except NotAnalogValueError:
            raise NotAnalogValueError(
                f"Step {fmt.expression(self.step)} of {self} does not evaluate to an "
                f"analog value"
            ) from None

        # Here we enforce that the values generated have the same format as the start
        # value.
        if isinstance(start, float):
            try:
                stop = _to_dimensionless_float(stop)
            except DimensionalityError:
                raise InvalidDimensionalityError(
                    f"Start {fmt.expression(self.start)} of {self} is "
                    f"dimensionless, but stop {fmt.expression(self.stop)} cannot "
                    f"be converted to dimensionless"
                ) from None
            try:
                step = _to_dimensionless_float(step)
            except DimensionalityError:
                raise InvalidDimensionalityError(
                    f"Step {fmt.expression(self.step)} of {self} is "
                    f"dimensionless, but stop {fmt.expression(self.stop)} cannot "
                    f"be converted to dimensionless"
                ) from None
            assert_type(start, float)
            assert_type(stop, float)
            assert_type(step, float)
            for value in numpy.arange(start, stop, step):
                yield float(value)
        elif isinstance(start, int):
            raise AssertionError("start must be strictly a float or a Quantity")
        else:
            try:
                stop = _to_unit(stop, start.units)
            except DimensionalityError as e:
                raise InvalidDimensionalityError(
                    f"Start {fmt.expression(self.start)} of {self} has invalid "
                    f"dimensionality."
                ) from e
            try:
                step = _to_unit(step, start.units)
            except DimensionalityError as e:
                raise InvalidDimensionalityError(
                    f"Step {fmt.expression(self.step)} of {self} has invalid "
                    f"dimensionality."
                ) from e
            assert_type(start, Quantity[float])
            assert_type(stop, Quantity[float])
            assert_type(step, Quantity[float])
            for value in numpy.arange(start.magnitude, stop.magnitude, step.magnitude):
                yield Quantity(float(value), start.units)


@attrs.define
class ExecuteShot:
    """Step that represents the execution of a shot."""

    def __str__(self):
        return "do shot"


def unstructure_hook(execute_shot: ExecuteShot):
    return {"execute": "shot"}


def structure_hook(data: str, cls: type[ExecuteShot]) -> ExecuteShot:
    return ExecuteShot()


serialization.register_unstructure_hook(ExecuteShot, unstructure_hook)

serialization.register_structure_hook(ExecuteShot, structure_hook)

"""TypeAlias for the different types of steps."""
Step: TypeAlias = ExecuteShot | VariableDeclaration | LinspaceLoop | ArangeLoop


def is_step(step) -> TypeGuard[Step]:
    return isinstance(
        step,
        (
            ExecuteShot,
            VariableDeclaration,
            LinspaceLoop,
            ArangeLoop,
        ),
    )


@attrs.define
class StepsConfiguration(IterationConfiguration):
    """Define the parameter iteration of a sequence as a list of steps.

    Attributes:
        steps: The steps of the iteration.
    """

    steps: list[Step] = attrs.field(
        validator=attrs.validators.deep_iterable(
            iterable_validator=attrs.validators.instance_of(list),
            member_validator=validate_step,
        ),
        on_setattr=attrs.setters.validate,
    )

    @classmethod
    def empty(cls) -> Self:
        return cls(steps=[])

    def expected_number_shots(self) -> int | Unknown:
        """Returns the expected number of shots that will be executed by the sequence.

        Returns:
            A positive integer if the number of shots can be determined, or Unknown if
            the number of shots cannot be determined.
        """

        return sum(expected_number_shots(step) for step in self.steps)

    def get_parameter_names(self) -> set[DottedVariableName]:
        return set().union(*[get_parameter_names(step) for step in self.steps])

    @classmethod
    def dump(cls, steps_configuration: StepsConfiguration) -> serialization.JSON:
        return serialization.unstructure(steps_configuration, StepsConfiguration)

    @classmethod
    def load(cls, data: serialization.JSON) -> StepsConfiguration:
        return serialization.structure(data, StepsConfiguration)

    def walk(self, initial_context: StepContext) -> Iterator[StepContext]:
        """Returns the context for every shot encountered while walking the steps."""

        return walk_steps(self.steps, initial_context)

    @override
    def get_parameter_schema(
        self, initial_parameters: Mapping[DottedVariableName, Parameter]
    ) -> ParameterSchema:
        context_iterator = self.walk(StepContext(initial_parameters))
        try:
            first_context = next(context_iterator)
        except StopIteration:
            # In case there is not steps to walk, we return a schema made only of the
            # initial constant parameters.
            return ParameterSchema(
                _constant_schema=initial_parameters, _variable_schema={}
            )
        variable_parameters = self.get_parameter_names()
        constant_parameters = set(initial_parameters) - variable_parameters
        constant_schema = {
            name: first_context.variables[name] for name in constant_parameters
        }
        initial_values = first_context.variables.to_flat_dict()
        variable_schema = {
            name: ParameterSchema.type_from_value(initial_values[name])
            for name in variable_parameters
        }
        return ParameterSchema(
            _constant_schema=constant_schema, _variable_schema=variable_schema
        )


@functools.singledispatch
def expected_number_shots(step: Step) -> int | Unknown:
    raise NotImplementedError(f"Cannot determine the number of shots for {step}")


@expected_number_shots.register
def _(step: VariableDeclaration):
    return 0


@expected_number_shots.register
def _(step: ExecuteShot):
    return 1


@expected_number_shots.register
def _(step: LinspaceLoop):
    sub_steps_number = sum(
        expected_number_shots(sub_step) for sub_step in step.sub_steps
    )
    return sub_steps_number * step.num


@expected_number_shots.register
def _(step: ArangeLoop):
    try:
        length = len(list(step.loop_values({})))
    except (EvaluationError, NotAnalogValueError, InvalidDimensionalityError):
        # The errors above can occur if the steps are still being edited or if the
        # expressions depend on other variables that are not defined here.
        # These can be errors on the user side, so we don't want to crash on them, and
        # we just indicate that we don't know the number of shots.
        return Unknown()

    sub_steps_number = sum(
        expected_number_shots(sub_step) for sub_step in step.sub_steps
    )
    return sub_steps_number * length


def get_parameter_names(step: Step) -> set[DottedVariableName]:
    match step:
        case VariableDeclaration(variable=variable, value=_):
            return {variable}
        case ExecuteShot():
            return set()
        case LinspaceLoop(variable=variable, sub_steps=sub_steps) | ArangeLoop(
            variable=variable, sub_steps=sub_steps
        ):
            return {variable}.union(
                *[get_parameter_names(sub_step) for sub_step in sub_steps]
            )
        case _:
            assert_never(step)


def wrap_error[
    S: Step
](
    function: Callable[[S, StepContext], Generator[StepContext, None, StepContext]]
) -> Callable[[S, StepContext], Generator[StepContext, None, StepContext]]:
    """Wrap a function that evaluates a step to raise nicer errors for the user."""

    @functools.wraps(function)
    def wrapper(step: S, context: StepContext):
        try:
            return function(step, context)
        except Exception as e:
            raise StepEvaluationError(f"Error while evaluating step <{step}>") from e

    return wrapper


def walk_steps(
    steps: Iterable[Step], initial_context: StepContext
) -> Iterator[StepContext]:
    """Yields the context for each shot defined by the steps.

    This function will recursively evaluate each step in the sequence passed as
    argument.
    Before executing the sequence, an empty context is initialized.
    The context holds the value of the parameters at a given point in the sequence.
    Each step has the possibility to update the context with new values.
    """

    context = initial_context

    for step in steps:
        context = yield from walk_step(step, context)


@functools.singledispatch
@wrap_error
def walk_step(
    step: Step, context: StepContext
) -> Generator[StepContext, None, StepContext]:
    """Iterates over the steps of a sequence.

    Args:
        step: the step of the sequence currently executed
        context: Contains the values of the variables before this step.

    Yields:
        The context for every shot encountered while walking the steps.

    Returns:
        The context after the step passed in argument has been executed.
    """

    raise NotImplementedError(f"Cannot walk step {step}")


# noinspection PyUnreachableCode
@walk_step.register
@wrap_error
def _(
    declaration: VariableDeclaration,
    context: StepContext,
) -> Generator[StepContext, None, StepContext]:
    """Execute a VariableDeclaration step.

    This step updates the context passed with the value of the variable declared.
    """

    value = declaration.value.evaluate(context.variables.dict())
    if not is_parameter(value):
        raise InvalidTypeError(
            f"{fmt.expression(declaration.value)}> does not evaluate to a parameter, "
            f"but to {fmt.type_(type(value))}.",
        )
    return context.update_variable(declaration.variable, value)

    # This code is unreachable, but it is kept here to make the function a generator.
    if False:
        yield context


@walk_step.register
@wrap_error
def _(
    arange_loop: ArangeLoop,
    context: StepContext,
) -> Generator[StepContext, None, StepContext]:
    """Loop over a variable in a numpy arange like loop.

    This function will loop over the variable defined in the arange loop and execute
    the sub steps for each value of the variable.

    Returns:
        A new context object containing the value of the arange loop variable after
        the last iteration, plus the values of the variables defined in the sub
        steps.
    """

    for value in arange_loop.loop_values(context.variables.dict()):
        context = context.update_variable(arange_loop.variable, value)
        for step in arange_loop.sub_steps:
            context = yield from walk_step(step, context)
    return context


@walk_step.register
@wrap_error
def _(
    linspace_loop: LinspaceLoop,
    context: StepContext,
) -> Generator[StepContext, None, StepContext]:
    """Loop over a variable in a numpy linspace like loop.

    This function will loop over the variable defined in the linspace loop and
    execute the sub steps for each value of the variable.

    Returns:
        A new context object containing the value of the linspace loop variable
        after the last iteration, plus the values of the variables defined in the
        sub steps.
    """

    for value in linspace_loop.loop_values(context.variables.dict()):
        context = context.update_variable(linspace_loop.variable, value)
        for step in linspace_loop.sub_steps:
            context = yield from walk_step(step, context)
    return context


@walk_step.register
@wrap_error
def _(
    shot: ExecuteShot, context: StepContext
) -> Generator[StepContext, None, StepContext]:
    """Schedule a shot to be run.

    This function schedule to run a shot on the experiment with the parameters
    defined in the context at this point.

    Returns:
        The context passed as argument unchanged.
    """

    yield context
    return context


class StepEvaluationError(Exception):
    pass


def _to_scalar_analog_value(value: Any) -> ScalarAnalogValue:
    """Attempt to convert a value to a scalar analog value.

    Raises:
        NotAnalogValueError: If the value can't be converted to a scalar analog value.
    """

    if isinstance(value, int):
        return float(value)
    if not is_scalar_analog_value(value):
        raise NotAnalogValueError(value)
    return value


def _to_dimensionless_float(value: ScalarAnalogValue) -> float:
    """Convert a scalar analog value to a dimensionless float.

    Raises:
        DimensionalityError: If the value is a quantity not commensurate with
        dimensionless.
    """

    if isinstance(value, Quantity):
        return value.to_unit(dimensionless).magnitude
    elif isinstance(value, float):
        return value
    elif isinstance(value, int):
        raise AssertionError("stop must be strictly a float or a Quantity")
    else:
        assert_never(value)


def _to_unit[U: Unit](value: ScalarAnalogValue, unit: U) -> Quantity[float, U]:
    """Convert a scalar analog value to the same unit as another.

    Raises:
        DimensionalityError: If the value is a quantity not commensurate with the unit.
    """

    if isinstance(value, float):
        value = Quantity(value, dimensionless)
    elif isinstance(value, int):
        raise AssertionError("stop must be strictly a float or a Quantity")
    return value.to_unit(unit)

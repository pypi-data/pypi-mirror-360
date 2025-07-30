"""This module contains the implementation of timed instructions."""

from ._instructions import (
    TimedInstruction,
    Concatenated,
    Repeated,
    Pattern,
    concatenate,
    InstrType,
)
from ._plot import plot_instruction
from ._ramp import create_ramp, Ramp
from ._stack import stack_instructions, merge_instructions
from ._to_graph import to_graph
from ._to_time_array import convert_to_change_arrays
from ._with_name import with_name

__all__ = [
    "TimedInstruction",
    "Concatenated",
    "Repeated",
    "Pattern",
    "convert_to_change_arrays",
    "with_name",
    "stack_instructions",
    "merge_instructions",
    "concatenate",
    "create_ramp",
    "Ramp",
    "plot_instruction",
    "to_graph",
    "InstrType",
]

"""WSE mathematical exercises."""

__all__ = [
    'AddingExercise',
    'DivisionExercise',
    'ExactOperandGenerator',
    'MultiplicationExercise',
    'RandomOperandGenerator',
    'SimpleCalcConfig',
    'SubtractionExercise',
]

from wse_exercises.core.math.base.components import SimpleCalcConfig
from wse_exercises.core.math.exercises import (
    AddingExercise,
    DivisionExercise,
    MultiplicationExercise,
    SubtractionExercise,
)
from wse_exercises.core.math.services.operand_generator import (
    ExactOperandGenerator,
    RandomOperandGenerator,
)

"""Core business logic package for WSE Exercise Series."""

__all__ = [
    'MathExercise',
    'MATH_EXERCISES',
]

from wse_exercises.core.math import (
    AddingExercise,
    DivisionExercise,
    MultiplicationExercise,
    SubtractionExercise,
)
from wse_exercises.core.math.enums import MathExercise

MATH_EXERCISES = {
    MathExercise.ADDING: AddingExercise,
    MathExercise.SUBTRACTION: SubtractionExercise,
    MathExercise.MULTIPLICATION: MultiplicationExercise,
    MathExercise.DIVISION: DivisionExercise,
}

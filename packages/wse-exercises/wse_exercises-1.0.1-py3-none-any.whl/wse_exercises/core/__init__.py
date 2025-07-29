"""Core business logic package for WSE Exercise Series."""

__all__ = [
    'Exercises',
    'EXERCISES',
]

from wse_exercises.core.math import (
    AddingExercise,
    DivisionExercise,
    MultiplicationExercise,
    SubtractionExercise,
)
from wse_exercises.core.math.enums import Exercises

EXERCISES = {
    Exercises.ADDING: AddingExercise,
    Exercises.SUBTRACTION: SubtractionExercise,
    Exercises.MULTIPLICATION: MultiplicationExercise,
    Exercises.DIVISION: DivisionExercise,
}

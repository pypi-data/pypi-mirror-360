"""Defines enumeration of available exercise types."""

from wse_exercises.base.enums import BaseEnum


class Exercises(BaseEnum):
    """Enumeration of available exercise types."""

    ADDING = 'adding'
    DIVISION = 'division'
    MULTIPLICATION = 'multiplication'
    SUBTRACTION = 'subtraction'

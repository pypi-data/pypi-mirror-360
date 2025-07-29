"""Defines protocol for Simple math exercise interface."""

from typing import Protocol

from wse_exercises.base.interfaces import ITask

from .task import (
    MathTaskConditions,
    MathTaskConfig,
    MathTextAnswer,
    MathTextQuestion,
)


class ISimpleCalcTask(
    ITask[
        MathTaskConfig,
        MathTaskConditions,
        MathTextQuestion,
        MathTextAnswer,
    ],
    Protocol,
):
    """Protocol for Simple math exercise interface."""

"""Defines the math task Data Transfer Objects."""

from typing import Any

from pydantic import validator

from wse_exercises.base.componets import (
    Answer,
    Question,
    TaskConditions,
    TaskConfig,
)
from wse_exercises.base.task import Task


class MathTaskConfig(TaskConfig):
    """Math task config."""

    min_value: int
    max_value: int

    @classmethod
    @validator('max_value')
    def check_min_less_than_max(
        cls,
        value: str,
        values: dict[str, Any],
    ) -> str:
        """Check that the minimum value is greater than the maximum."""
        if 'min_value' in values and value <= values['min_value']:
            raise ValueError('max_value must be greater than min_value')
        return value


class MathTaskConditions(TaskConditions):
    """Math task conditions."""

    operand_1: int
    operand_2: int


class MathTextQuestion(Question):
    """Math text task question."""

    text: str


class MathTextAnswer(Answer):
    """Math text task answer."""

    text: str


class SimpleMathTask(
    Task[
        MathTaskConfig,
        MathTaskConditions,
        MathTextQuestion,
        MathTextAnswer,
    ]
):
    """Base simple math task with text question/answer.

    :param config: Contains the min and max values of the operands.
    :param conditions: Contain the first and second operand values.
    :param question: The text representation of question.
    :param answer: The text representation of answer.
    :param exercise_name: Exercise name.
    :param created: The data and time of task creation.
    :param error_msg: The task creation error message.
    """

    config: MathTaskConfig
    conditions: MathTaskConditions
    question: MathTextQuestion
    answer: MathTextAnswer

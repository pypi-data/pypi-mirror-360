"""Defines base class for task."""

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

from wse_exercises.core.math.enums import Exercises

from .mixins import ConvertMixin

T = TypeVar('T', bound='Task[Any, Any, Any, Any]')

AnswerT = TypeVar('AnswerT')
QuestionT = TypeVar('QuestionT')
TaskConfigT = TypeVar('TaskConfigT')
TaskConditionsT = TypeVar('TaskConditionsT')


class Task(
    ConvertMixin,
    BaseModel,
    Generic[TaskConfigT, TaskConditionsT, QuestionT, AnswerT],
):
    """Base class for DTO exercise task."""

    config: TaskConfigT
    conditions: TaskConditionsT
    question: QuestionT
    answer: AnswerT
    exercise_name: Exercises
    created: datetime = Field(default_factory=datetime.now)
    error_msg: str = Field(default='', frozen=True)

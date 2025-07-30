"""Defines base class for task."""

from datetime import datetime, timezone
from typing import Generic, TypeVar

from pydantic import Field

from .components import Answer, Conditions, Config, Question
from .enums import Exercise
from .model import BaseShema

ConfigT = TypeVar('ConfigT', bound=Config)
ConditionsT = TypeVar('ConditionsT', bound=Conditions)
QuestionT = TypeVar('QuestionT', bound=Question)
AnswerT = TypeVar('AnswerT', bound=Answer)
ExerciseT = TypeVar('ExerciseT', bound=Exercise)


class Task(
    BaseShema,
    Generic[ConfigT, ConditionsT, QuestionT, AnswerT, ExerciseT],
):
    """Base class for DTO exercise task."""

    config: ConfigT
    conditions: ConditionsT
    question: QuestionT
    answer: AnswerT
    exercise_name: ExerciseT
    created: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

"""Base interface."""

from datetime import datetime
from typing import Any, Protocol, Type, TypeVar

from wse_exercises.core.math.enums import Exercises

from .componets import (
    Answer,
    Question,
    TaskConditions,
    TaskConfig,
)

TaskConfigT = TypeVar('TaskConfigT', bound=TaskConfig)
TaskConditionsT = TypeVar('TaskConditionsT', bound=TaskConditions)
QuestionT = TypeVar('QuestionT', bound=Question)
AnswerT = TypeVar('AnswerT', bound=Answer)

ExerciseConfigT = TypeVar('ExerciseConfigT')

T = TypeVar('T', bound='ITask[Any, Any, Any, Any]')


class IConvertMixin(Protocol):
    """Protocol for dict/json conversion interface."""

    @classmethod
    def from_dict(cls: Type[T], data: dict[str, Any]) -> T:
        """Instantiate the class from a dictionary of attributes."""

    @classmethod
    def from_json(cls: Type[T], data: str | bytes) -> T:
        """Instantiate the class from a JSON string or bytes."""

    def to_dict(self) -> dict[str, Any]:
        """Convert the instance to a dictionary."""

    def to_json(self) -> str:
        """Serialize the instance to a JSON string."""


class ITask(
    IConvertMixin,
    Protocol[
        TaskConfigT,
        TaskConditionsT,
        QuestionT,
        AnswerT,
    ],
):
    """The interface of the task."""

    config: TaskConfigT
    conditions: TaskConditionsT
    question: QuestionT
    answer: AnswerT
    exercise_name: Exercises
    created: datetime
    error_msg: str


class ITaskRequest(
    IConvertMixin,
    Protocol[ExerciseConfigT],
):
    """Protocol for request task DTO."""

    name: Exercises
    config: ExerciseConfigT


class IExerciseConfig(
    IConvertMixin,
    Protocol,
):
    """Protocol for exercise base config interface."""


class IExercise(
    Protocol,
):
    """Protocol for exercise interface."""

    def create_task(
        self,
        config: IExerciseConfig | dict[str, Any] | None = None,
    ) -> ITask[
        TaskConfig,
        TaskConditions,
        Question,
        Answer,
    ]:
        """Create simple calculation task."""

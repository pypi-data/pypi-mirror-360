"""Defines pydantic v1 models for REST API."""

from typing import Any, Generic, TypeVar

from .model import BaseShema
from .task import AnswerT, ConfigT, ExerciseT, Task

TaskT = TypeVar('TaskT', bound=Task[Any, Any, Any, Any, Any])


class TaskRequest(BaseShema, Generic[ExerciseT, ConfigT]):
    """Model for request the task.

    :param Exercise name: Exercise name.
    :param ExerciseConfig config: Exercise configuration.
    """

    name: ExerciseT
    config: ConfigT


class TaskResponse(BaseShema, Generic[TaskT]):
    """Response model with crated task.

    :param str uid: The unique identifier of task.
    :param TaskT task: Created task.
    """

    uid: str
    task: TaskT


class HandleAnswer(BaseShema, Generic[AnswerT]):
    """Model for request the answer handling.

    :param str uid: The unique identifier of task.
    :param AnswerT answer: Answer to handle.
    """

    uid: str
    answer: AnswerT

"""Defines pydantic v1 models for simple calc math task REST API."""

from wse_exercises.base.components import TextAnswer
from wse_exercises.base.rest import (
    HandleAnswer,
    TaskRequest,
    TaskResponse,
)

from . import SimpleCalcConfig
from .enums import MathExercise
from .task import SimpleCalcTask


class SimpleCalcRequest(TaskRequest[MathExercise, SimpleCalcConfig]):
    """Model for request the simple calculation task."""

    name: MathExercise
    config: SimpleCalcConfig


class SimpleCalcResponse(TaskResponse[SimpleCalcTask]):
    """Response model with crated simple calculation task."""

    task: SimpleCalcTask


class SimpleCalcHandle(HandleAnswer[TextAnswer]):
    """Model for request the answer handling of simple calculation."""

    answer: TextAnswer

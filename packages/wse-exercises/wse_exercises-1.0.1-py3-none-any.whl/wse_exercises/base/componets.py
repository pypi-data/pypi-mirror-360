"""Defines base task DTO components."""

from pydantic import BaseModel

from .mixins import ConvertMixin


class TaskConfig(
    ConvertMixin,
    BaseModel,
):
    """Base config."""


class TaskConditions(
    ConvertMixin,
    BaseModel,
):
    """Base conditions."""


class Question(
    ConvertMixin,
    BaseModel,
):
    """Base question."""


class Answer(
    ConvertMixin,
    BaseModel,
):
    """Base answer."""

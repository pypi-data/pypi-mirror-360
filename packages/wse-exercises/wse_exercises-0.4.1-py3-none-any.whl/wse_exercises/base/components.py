"""Defines base task components."""

from .model import BaseShema


class Config(BaseShema):
    """Base exercise config model to create task."""


class Conditions(BaseShema):
    """Base exercise conditions model to create task."""


class Question(BaseShema):
    """Base task question model."""


class Answer(BaseShema):
    """Base task answer model."""


class TextQuestion(Question):
    """Text representation of question.

    :param str text: Text question.
    """

    text: str


class TextAnswer(Answer):
    """Text representation of answer.

    :param str text: Text answer.
    """

    text: str

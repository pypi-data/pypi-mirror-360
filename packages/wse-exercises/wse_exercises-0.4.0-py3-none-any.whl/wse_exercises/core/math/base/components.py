"""Defines mathematical task components."""

from typing import Any

from pydantic import validator

from wse_exercises.base.components import Conditions, Config

MIN_VALUE = 1
MAX_VALUE = 9


class SimpleCalcConfig(Config):
    """Exercise config to create simple calculation task."""

    min_value: int = MIN_VALUE
    max_value: int = MAX_VALUE

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


class SimpleCalcConditions(Conditions):
    """Exercise conditions to create simple calculation math task."""

    operand_1: int
    operand_2: int

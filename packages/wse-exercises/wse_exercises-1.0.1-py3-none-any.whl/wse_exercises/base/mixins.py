"""Defines mixins."""

from datetime import datetime
from typing import Any, Type, TypeVar

from pydantic import BaseModel

T = TypeVar('T', bound='ConvertMixin')


class ConvertMixin(BaseModel):
    """Mixin providing conversion between dict/json."""

    @classmethod
    def from_dict(cls: Type[T], data: dict[str, Any]) -> T:
        """Instantiate the class from a dictionary of attributes."""
        return cls.parse_obj(data)

    @classmethod
    def from_json(cls: Type[T], data: str | bytes) -> T:
        """Instantiate the class from a JSON string or bytes."""
        return cls.parse_raw(data)

    def to_dict(self) -> dict[str, Any]:
        """Convert the instance to a dictionary."""

        def convert_datetime(data: dict[str, Any]) -> dict[str, Any]:
            dict_data: dict[str, Any] = {}

            for key, value in data.items():
                if isinstance(value, datetime):
                    dict_data[key] = value.isoformat()
                elif isinstance(value, dict):
                    dict_data[key] = convert_datetime(value)
                else:
                    dict_data[key] = value

            return dict_data

        return convert_datetime(self.dict())

    def to_json(self) -> str:
        """Serialize the instance to a JSON string."""
        return self.json()

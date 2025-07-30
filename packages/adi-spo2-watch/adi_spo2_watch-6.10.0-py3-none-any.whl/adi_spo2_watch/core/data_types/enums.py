import logging
from enum import Enum
from typing import List
from .integer import Int
from .data_type import DataType

logger = logging.getLogger(__name__)


class Enums(DataType):

    def __init__(self, size: int, enum_class: callable, reverse: bool = False, default=None, decode_with_int=False):
        super().__init__(size, reverse, default)
        self._enum_class = enum_class
        self._decode_with_int = decode_with_int
        self._enum_list = [e for e in self._enum_class]

    def encode(self):
        result = [] if self.get_value() is None else self.get_value().value
        if not len(result) == self.get_size():
            result = result + [0] * (self.get_size() - len(result))
        return list(reversed(result)) if self._reverse else result

    def decode(self, array: List):
        array = list(reversed(array)) if self._reverse else array
        if self._decode_with_int:
            int_val = Int(self.get_size())
            int_val.decode(array)
            array = [int_val.get_value()]
        try:
            self.set_value(self._enum_class(array))
        except ValueError as _:
            generated_enum = f"FAILED_TO_DECODE :: {self._enum_class}"
            invalid_enum = Enum("InvalidEnum", [(generated_enum, array)])
            self.set_value(list(invalid_enum)[0])

    def _default_value(self):
        return self._enum_list[0]

    def _value_check(self, value: Enum):
        if not type(value) == Enum:
            self.set_value(self._default_value())
            logger.error(f"{value} is not of type Enum. Using default value {self._default_value()}.")
            return False

        if value not in self._enum_list:
            logger.error(f"{value} doesn't belongs to enum class {self._enum_class}."
                         f" Using default value {self._default_value()}.")
            return False

        return True

import logging
from typing import List

from .data_type import DataType

logger = logging.getLogger(__name__)


class String(DataType):

    def __init__(self, size: int, reverse: bool = False, default: str = ""):
        super().__init__(size, reverse, default)

    def encode(self):
        result = [ord(char) for char in self.get_value()]
        if not self.get_size() == -1:
            result = result[:self.get_size()]
            result = result + [0 for _ in range(self.get_size() - len(result))]
        return result

    def decode(self, array: List):
        result = ""
        for val in array:
            if val == 0x0:
                break
            result += chr(val)
        self.set_value(str(result))

    def default_value(self):
        return self.set_value("")

    def _value_check(self, value: str):
        if not type(value) == str:
            self.default_value()
            logger.error(f"{value} is not of type str. Using default value {self.get_value()}.")
            return False

        return True

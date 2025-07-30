import struct
import logging
from typing import List
from .data_type import DataType

logger = logging.getLogger(__name__)


class Decimal(DataType):

    def __init__(self, size, reverse: bool = False, value_range: List = None, default: float = 0.0):
        super().__init__(size, reverse, default)
        self._value_range = value_range

    def encode(self):
        result = list(struct.pack("f", self.get_value()))
        return reversed(result) if self._reverse else result

    def decode(self, array: List):
        array = reversed(array) if self._reverse else array
        self.set_value(struct.unpack("f", bytes(array))[0])

    def default_value(self):
        return self.encode(self._default)

    def _value_check(self, value: float):
        if not type(value) == float:
            logger.error(f"{value} is not of type float. Using default value {self._default}.")
            return False

        if self._value_range:
            if not self._value_range[0] <= value <= self._value_range[1]:
                logger.error(f"{'0x%X' % value} is out of range, value needs to be greater than or equal to "
                             f"{'0x%X' % self._value_range[0]} and less than or equal to "
                             f"{'0x%X' % self._value_range[1]}.")
                return False

        return True

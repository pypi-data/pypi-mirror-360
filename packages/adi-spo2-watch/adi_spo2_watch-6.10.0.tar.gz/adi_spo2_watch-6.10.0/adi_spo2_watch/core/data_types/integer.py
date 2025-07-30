import logging
from typing import List

from .data_type import DataType
from .. import utils

logger = logging.getLogger(__name__)


class Int(DataType):

    def __init__(self, size: int, sign: bool = False, reverse: bool = False, value_limit: List = None,
                 default: int = None, to_hex: bool = False, encode_on_none: bool = True):
        super().__init__(size, reverse, default)
        self._sign = sign
        self._to_hex = to_hex
        self._value_limit = value_limit
        self._encode_on_none = encode_on_none

    def encode(self):
        value = self.get_value()
        if value is None and not self._encode_on_none:
            return []
        self._value_check()
        return utils.split_int_in_bytes(self.get_value(), length=self._size, reverse=self._reverse)

    def decode(self, array: List):
        value = utils.join_multi_length_packets(
            array, sign=self._sign, reverse=self._reverse,
            convert_to_hex=self._to_hex
        )
        self.set_value(value)

    def _default_value(self):
        self.set_value(0)

    def _value_check(self):
        value = self.get_value()

        if value is None:
            self._default_value()
            return

        if not type(value) == int:
            self._default_value()
            logger.error(f"{value} is not of type int. Using default value {self.get_value()}.")
            return False

        if self._value_limit:
            if not self._value_limit[0] <= value <= self._value_limit[1]:
                logger.error(f"{'0x%X' % value} is out of range, value needs to be greater than or equal to "
                             f"{'0x%X' % self._value_limit[0]} and less than or equal to "
                             f"{'0x%X' % self._value_limit[1]}.")
                return False

        lower_bound = 0
        upper_bound = 16 ** (self._size * 2) - 1
        if self._sign:
            lower_bound = -(16 ** ((self._size - 1) * 2))
            upper_bound = 16 ** ((self._size - 1) * 2) - 1

        if not lower_bound <= value <= upper_bound:
            logger.error(f"{'0x%X' % value} is out of range, value needs to be greater than or equal to "
                         f"{'0x%X' % lower_bound} and less than or equal to {'0x%X' % upper_bound}.")
            return False

        return True

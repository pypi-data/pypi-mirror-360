from typing import List

from .. import utils
from .data_type import DataType

import logging

logger = logging.getLogger(__name__)


class Binary(DataType):

    def __init__(self, size: int):
        super().__init__(size, False, False)

    def encode(self):
        return utils.split_int_in_bytes(self.get_value(), length=self._size, reverse=self._reverse)

    def decode(self, array: List):
        value = utils.join_multi_length_packets(array, reverse=self._reverse)
        self.set_value(bool(value))
        # none if value not in [0,1]

    def _default_value(self):
        self.set_value(False)

    def _value_check(self, value: int):
        if not type(value) == bool:
            self._default_value()
            logger.error(f"{value} is not of type boolean. Using default value {self.get_value()}.")
            return False

        return True

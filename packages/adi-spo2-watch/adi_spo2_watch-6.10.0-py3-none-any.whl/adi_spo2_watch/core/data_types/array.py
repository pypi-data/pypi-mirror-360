import logging
from typing import List
from .data_type import DataType

logger = logging.getLogger(__name__)


class Array(DataType):

    def __init__(self, size: int, reverse_inner_array=None, dimension: int = 1, data_types: List = None,
                 size_limit: int = None, default=None):
        super().__init__(size, reverse_inner_array, default)
        self._dimension = dimension
        self._data_types = data_types
        self._size_limit = size_limit

    def encode(self):
        result = []
        value = self.get_value()
        if value is None:
            return result
        self.reverse_pair_check(value)
        for val in value:
            for i in range(self._dimension):
                temp_val = val if self._dimension == 1 else val[i]
                data_type = self._data_types[i]
                data_type.set_value(temp_val)
                result += data_type.encode()
        return result

    def decode(self, array: List):
        result = []
        total_size = 0
        while not len(array) == 0:
            inner_result = []
            for i in range(self._dimension):
                data_type = self._data_types[i]
                data_size = data_type.get_size()
                total_size += data_size
                value = array[:data_size]
                array = array[data_size:]
                data_type.decode(value)
                inner_result.append(data_type.get_value())
            result.append(inner_result)
        if self._dimension == 1:
            result = [res[0] for res in result]
        self.reverse_pair_check(result)
        self._size = total_size
        self.set_value(result)

    def reverse_pair_check(self, result):
        if self._dimension > 1 and self._reverse:
            for res in result:
                res.reverse()

    def default_value(self):
        return self.encode(self._default)

    def _value_check(self, value: List):
        if not type(value) == list:
            logger.error(f"{value} is not of type list. Using default value {self._default}.")
            return False

        if self._size_limit:
            if len(value) > self._size_limit:
                logger.error(f"Max length of {value} can be {self._size_limit}.")
                return False
        return True

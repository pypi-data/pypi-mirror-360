class DataType:

    def __init__(self, size, reverse, default):
        self._size = size
        self._value = default
        self._reverse = reverse

    def get_size(self):
        return self._size

    def set_value(self, value):
        self._value = value

    def get_value(self):
        return self._value

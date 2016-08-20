import random

from mongoframes.factory.makers import Maker

__all__ = [
    'Counter'
    ]


class Counter(Maker):
    """
    Generate a sequence of numbers.
    """

    def __init__(self, start_from=1, step=1):
        super().__init__()

        self._start_from = int(start_from)
        self._step = step
        self._counter = self._start_from

    def reset(self):
        self._counter = int(self._start_from)

    def _assemble(self):
        value = self._counter
        self._counter += int(self._step)
        return value


class Float(Maker):
    """
    Generate a random float between two values.
    """

    def __init__(self, min_value, max_value):
        super().__init__()

        self._min_value = min_value
        self._max_value = max_value

    def _assemble(self):
        return random.uniform(float(self._min_value), float(self._max_value))


class Int(Float):
    """
    Generate a random integer between two values.
    """

    def _assemble(self):
        return random.randint(int(self._min_value), int(self._max_value))
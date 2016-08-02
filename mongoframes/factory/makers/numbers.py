from mongoframes.factory.makers import Maker

__all__ = [
    'Counter'
    ]


class Counter(Maker):
    """
    Generate a sequence of numbers.
    """

    def __init__(self, start_from=1, step=1):
        self._start_from = int(start_from)
        self._step = step
        self._counter = self._start_from

    def reset(self):
        self._counter = int(self._start_from)

    def _assemble(self):
        value = self._counter
        self._counter += int(self._step)
        return value
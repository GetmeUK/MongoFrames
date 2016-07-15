import random

__all__ = [
    'RandomQuota'
    ]


class Quota:
    """
    A base class for implementing variable quota (although the base class
    provides a fixed value and is no difference over sending a integer or float
    value).

    The `Quota` class can be safely used as an argument for `Factory`s and
    `Maker`s.
    """

    def __init__(self, quantity):
        self._quantity = 0

    def __int__(self):
        return int(self._quantity)

    def __float__(self):
        return float(self._quantity)


class RandomQuota:
    """
    Return a random quota between two values.
    """

    def __init__(self, min_quantity, max_quantity):
        self._min_quantity = min_quantity
        self._max_quantity = max_quantity

    def __int__(self):
        return random.randint(self._min_quantity, self._max_quantity)

    def __float__(self):
        return random.uniform(self._min_quantity, self._max_quantity)

# @@
# - WeightedQuota
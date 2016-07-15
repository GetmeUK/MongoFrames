import random

__all__ = [
    'RandomQuantity'
    ]


class Quantity:
    """
    A base class for implementing variable quantities (although the base class
    provides a fixed value and is no difference over sending a integer or float
    value).

    The `quantity` class can be used as an argument for `Quota`s and `Maker`s.
    """

    def __init__(self, quantity):
        self._quantity = 0

    def __int__(self):
        return int(self._quantity)

    def __float__(self):
        return float(self._quantity)


class RandomQuantity:
    """
    Return a random quantity between two numbers.
    """

    def __init__(self, min_quantity, max_quantity):
        self._min_quantity = min_quantity
        self._max_quantity = max_quantity

    def __int__(self):
        return random.randint(self._min_quantity, self._max_quantity)

    def __float__(self):
        return random.uniform(self._min_quantity, self._max_quantity)
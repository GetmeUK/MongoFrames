import random

__all__ = [
    'Gauss',
    'Random'
    ]


class Quota:
    """
    A base class for implementing variable quota (although the base class
    provides a fixed value and is no different than using an integer or float
    value).

    The Quota class can be safely used as an argument for `Factory`s and
    `Maker`s.
    """

    def __init__(self, quantity):
        self._quantity = quantity

    def __int__(self):
        return int(self._quantity)

    def __float__(self):
        return float(self._quantity)


class Gauss(Quota):
    """
    Return a random quota using a Gaussian distribution.
    """

    def __init__(self, mu, sigma):
        self._mu = mu
        self._sigma = sigma

    def __int__(self):
        return int(float(self))

    def __float__(self):
        return random.gauss(self._mu, self._sigma)


class Random(Quota):
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
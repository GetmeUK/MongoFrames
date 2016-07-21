import random

from mongoframes.factory.makers import Maker

__all__ = [
    'OneOf'
    ]


class OneOf(Maker):
    """
    Pick one maker from a list of makers or values.
    """

    def __init__(self, items, weights=None):

        # The list of makers/values to select from
        self._items = items

        # The weighting to apply when selecting a maker/value
        self._weights = weights

    def _assemble(self):
        # Select an item
        item_index = 0
        if self._weights:
            item_index = self.weighted(self._weights)
        else:
            item_index = random.randint(0, len(self._items) - 1)

        # Return the index of the maker we selected and it's assemble output
        item = self._items[item_index]
        if isinstance(item, Maker):
            return [item_index, item._assemble()]
        return [item_index, item]

    def _finish(self, value):
        item = self._items[value[0]]
        if isinstance(item, Maker):
            return item._finish(value[1])
        return item

    @staticmethod
    def weighted(weights):
        """
        Return a random integer 0 <= N <= len(weights) - 1, where the weights
        determine the probability of each possible integer.

        Based on this StackOverflow post by Ned Batchelder:

        http://stackoverflow.com/questions/3679694/a-weighted-version-of-random-choice
        """
        choice = random.uniform(0, sum(weights))
        position = 0
        for i, weight in enumerate(weights):
            if position + weight >= choice:
                return i
            position += weight

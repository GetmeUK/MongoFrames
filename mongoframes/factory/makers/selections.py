import random

from mongoframes.factory.makers import Maker

__all__ = [
    'OneOf',
    'SomeOf'
    ]


class OneOf(Maker):
    """
    Pick one item from a list of makers or values.
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

        # Return the index and it's assembled value
        item = self._items[item_index]
        if isinstance(item, Maker):
            return [item_index, item._assemble()]
        return [item_index, None]

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


class SomeOf(Maker):
    """
    Pick one or more items from a list of makers or values.
    """

    # @@ Consider adding an allow duplicates option

    def __init__(self, items, sample_size, weights=None):

        # The list of makers/values to select from
        self._items = items

        # The number of items to pick
        self._sample_size = sample_size

        # The weighting to apply when selecting a maker/value
        self._weights = weights

    def _assemble(self):
        # Select some items
        sample_size = int(self._sample_size)

        sample_indexes = []
        if self._weights:
            sample_indexes = self.weighted(self._weights, sample_size)
        else:
            sample_indexes = random.sample(range(0, sample_size), sample_size)

        # Return the sampled indexes and their assembled values
        values = []
        for sample_index in sample_indexes:
            item = self._items[sample_index]
            if isinstance(item, Maker):
                values.append([sample_index, item._assemble()])
            else:
                values.append([sample_index, None])

        return values

    def _finish(self, value):
        values = []
        for sample in value:
            item = self._items[sample[0]]
            if isinstance(item, Maker):
                values.append(item._finish(sample[1]))
            else:
                values.append(item)
        return values

    @staticmethod
    def weighted(weights, sample_size):
        """
        Return a set of random integers 0 <= N <= len(weights) - 1, where the
        weights determine the probability of each possible integer in the set.
        """
        assert sample_size <= weights, "The sample size must be smaller than \
or equal to the number of weights it's taken from."

        samples = []
        while len(samples) < sample_size:
            # Pick a sample
            sample = OneOf.weighted(weights)

            # Remove it from the list of weights
            del weights[sample]

            # Add the sample to our samples
            samples.append(sample)
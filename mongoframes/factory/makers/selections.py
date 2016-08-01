import random

from mongoframes.factory.makers import Maker

__all__ = [
    'Cycle',
    'OneOf',
    'SomeOf'
    ]


class Cycle(Maker):
    """
    Pick the next item from a list of makers or values cycling through the list
    and repeating when we reach the end.
    """

    def __init__(self, items):

        # The list of makers/values to select from
        self._items = items

        # The index of the item that will be returned next
        self._item_index = 0

    def reset(self):
        """Reset the item index"""
        self._item_index = 0

    def _assemble(self):
        # Select the next item
        item_index = self._item_index
        item = self._items[item_index]

        # Move the index on 1 (and wrap it if we are at the end of the list)
        self._item_index += 1
        if self._item_index >= len(self._items):
            self._item_index = 0

        # Return the index and it's assembled value
        if isinstance(item, Maker):
            return [item_index, item._assemble()]
        return [item_index, None]

    def _finish(self, value):
        item = self._items[value[0]]
        if isinstance(item, Maker):
            return item._finish(value[1])
        return item


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

        # Convert weights to floats
        weights = [float(w) for w in weights]

        # Pick a value at random
        choice = random.uniform(0, sum(weights))

        # Find the value
        position = 0
        for i, weight in enumerate(weights):
            if position + weight >= choice:
                return i
            position += weight


class SomeOf(Maker):
    """
    Pick one or more items from a list of makers or values.
    """

    def __init__(
            self,
            items,
            sample_size,
            weights=None,
            with_replacement=False
            ):

        # The list of makers/values to select from
        self._items = items

        # The number of items to pick
        self._sample_size = sample_size

        # The weighting to apply when selecting a maker/value
        self._weights = weights

        # A flag indicating if the same item can be selected from the list more
        # than once.
        self._with_replacement = with_replacement

    def _assemble(self):
        # Select some items
        sample_size = int(self._sample_size)

        sample_indexes = []
        if self._weights:
            sample_indexes = self.weighted(
                self._weights,
                sample_size,
                with_replacement=self._with_replacement
                )
        else:
            sample_range = range(0, sample_size)
            if self._with_replacement:
                sample_indexes = [random.choice(sample_range) \
                    for s in range(0, sample_size)]
            else:
                sample_indexes = random.sample(sample_range, sample_size)

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
    def weighted(weights, sample_size, with_replacement=False):
        """
        Return a set of random integers 0 <= N <= len(weights) - 1, where the
        weights determine the probability of each possible integer in the set.
        """
        assert sample_size <= weights, "The sample size must be smaller than \
or equal to the number of weights it's taken from."

        # Convert weights to floats
        weights = [float(w) for w in weights]

        samples = []
        while len(samples) < sample_size:
            # Choice a weight
            weight = OneOf.weighted(weights)

            if not with_replacement:
                # Remove the weight from the list of weights we can select from
                del weights[weight]

            # Add the choosen weight to our samples
            samples.append(weight)

        return samples
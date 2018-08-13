from functools import reduce
import itertools
import math
import random

from mongoframes.factory.makers import Maker
from mongoframes import ASC

__all__ = [
    'Cycle',
    'OneOf',
    'RandomReference',
    'SomeOf'
    ]


class Cycle(Maker):
    """
    Pick the next item from a list of makers and/or values cycling through the
    list and repeating when we reach the end.
    """

    def __init__(self, items):
        super().__init__()

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
            with item.target(self.document):
                return item._finish(value[1])
        return item


class OneOf(Maker):
    """
    Pick one item from a list of makers and/or values.
    """

    def __init__(self, items, weights=None):
        super().__init__()

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
            with item.target(self.document):
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


class RandomReference(Maker):
    """
    Pick a reference document at random from a collection (determined by the
    given frame_cls) optionally applying a constraint.
    """

    def __init__(self, frame_cls, constraint=None):
        super().__init__()

        # The frame class that will be used to select a reference with
        self._frame_cls = frame_cls

        # The constraint applied when select a reference document
        self._constraint = constraint or {}

    def _assemble(self):
        # Select a random float that will be used to select a reference document
        # by it's position.
        return random.random()

    def _finish(self, value):
        # Count the number of documents available to pick from
        total_documents = self._frame_cls.count(self._constraint)

        # Calculate the position of the document we've picked
        position = math.floor(total_documents * value)

        # Select the document
        document = self._frame_cls.one(
            self._constraint,
            limit=1,
            skip=position,
            sort=[('_id', ASC)],
            projection={'_id': True}
            )

        # Check the document was found
        if document:
            return document._id

        return None


class SomeOf(Maker):
    """
    Pick one or more items from a list of makers and/or values.
    """

    def __init__(
            self,
            items,
            sample_size,
            weights=None,
            with_replacement=False
            ):
        super().__init__()

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
            sample_range = range(0, len(self._items))
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
                with item.target(self.document):
                    values.append(item._finish(sample[1]))
            else:
                values.append(item)
        return values

    @staticmethod
    def p(i, sample_size, weights):
        """
        Given a weighted set and sample size return the probabilty that the
        weight `i` will be present in the sample.

        Created to test the output of the `SomeOf` maker class. The math was
        provided by Andy Blackshaw - thank you dad :)
        """

        # Determine the initial pick values
        weight_i = weights[i]
        weights_sum = sum(weights)

        # Build a list of weights that don't contain the weight `i`. This list will
        # be used to build the possible picks before weight `i`.
        other_weights = list(weights)
        del other_weights[i]

        # Calculate the probability
        probability_of_i = 0
        for picks in range(0, sample_size):

            # Build the list of possible permutations for this pick in the sample
            permutations = list(itertools.permutations(other_weights, picks))

            # Calculate the probability for this permutation
            permutation_probabilities = []
            for permutation in permutations:

                # Calculate the probability for each pick in the permutation
                pick_probabilities = []
                pick_weight_sum = weights_sum

                for pick in permutation:
                    pick_probabilities.append(pick / pick_weight_sum)

                    # Each time we pick we update the sum of the weight the next
                    # pick is from.
                    pick_weight_sum -= pick

                # Add the probability of picking i as the last pick
                pick_probabilities += [weight_i / pick_weight_sum]

                # Multiply all the probabilities for the permutation together
                permutation_probability = reduce(
                    lambda x, y: x * y, pick_probabilities
                    )
                permutation_probabilities.append(permutation_probability)

            # Add together all the probabilities for all permutations together
            probability_of_i += sum(permutation_probabilities)

        return probability_of_i

    @staticmethod
    def weighted(weights, sample_size, with_replacement=False):
        """
        Return a set of random integers 0 <= N <= len(weights) - 1, where the
        weights determine the probability of each possible integer in the set.
        """
        assert sample_size <= len(weights), "The sample size must be smaller \
than or equal to the number of weights it's taken from."

        # Convert weights to floats
        weights = [float(w) for w in weights]
        weight_indexes = list(range(0, len(weights)))

        samples = []
        while len(samples) < sample_size:
            # Choice a weight
            sample = OneOf.weighted(weights)

            # Add the choosen weight to our samples
            samples.append(weight_indexes[sample])

            if not with_replacement:
                # Remove the weight from the list of weights we can select from
                del weights[sample]
                del weight_indexes[sample]

        return samples



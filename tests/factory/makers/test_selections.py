import random

from mongoframes.factory import makers
from mongoframes.factory import quotas
from mongoframes.factory.makers import selections as selection_makers

from tests.fixtures import *


def test_cycle():
    """
    `Cycle` makers should return values from a list of items (python types of or
    makers) one after another.
    """

    # Configured to cycle through a list of python types
    maker = selection_makers.Cycle(['foo', 'bar', 'zee'])

    for i, value in enumerate(['foo', 'bar', 'zee']):
        # Check the assembled result
        assembled = maker._assemble()
        assert assembled == [i, None]

        # Check the finished result
        finished = maker._finish(assembled)
        assert finished == value

    # Configured to cycle throguh a list of makers
    maker = selection_makers.Cycle([
        makers.Static('foo'),
        makers.Static('bar'),
        makers.Static('zee')
        ])

    for i, value in enumerate(['foo', 'bar', 'zee']):
        # Check the assembled result
        assembled = maker._assemble()
        assert assembled == [i, value]

        # Check the finished result
        finished = maker._finish(assembled)
        assert finished == value


def test_one_of():
    """
    `OneOf` makers should return one value at random (optionally weighted) from
    a list of items (python types of or makers).
    """

    # Seed the random generator to ensure test results are consistent
    random.seed(110679)

    # Configured to return an item from a list of python types
    maker = selection_makers.OneOf(['foo', 'bar', 'zee'])

    counts = {'foo': 0 , 'bar': 0, 'zee': 0}
    for i in range(0, 1000):
        # Check the assembled result
        assembled = maker._assemble()
        assert assembled[0] in [0, 1, 2] and assembled[1] == None

        # Check the finished result
        finished = maker._finish(assembled)
        assert finished in ['foo', 'bar', 'zee']

        # Count the occurances
        counts[finished] += 1

    # Confirm the counts are as approx. evenly distributed
    for value in ['foo', 'bar', 'zee']:
        assert int(round(counts[value] / 100)) == 3

    # Configured to return an item from a list of makers
    maker = selection_makers.OneOf([
        makers.Static('foo'),
        makers.Static('bar'),
        makers.Static('zee')
        ])

    counts = {'foo': 0 , 'bar': 0, 'zee': 0}
    for i in range(0, 1000):
        # Check the assembled result
        assembled = maker._assemble()
        assert assembled[0] in [0, 1, 2]
        assert assembled[1] in ['foo', 'bar', 'zee']

        # Check the finished result
        finished = maker._finish(assembled)
        assert finished in ['foo', 'bar', 'zee']

        # Count the occurances
        counts[finished] += 1

    # Confirm the counts are as approx. evenly distributed
    for value in ['foo', 'bar', 'zee']:
        assert int(counts[value] / 100) == 3

    # Configured to return using a weighted bias
    maker = selection_makers.OneOf(
        ['foo', 'bar', 'zee'],
        [quotas.Quota(10), quotas.Quota(30), quotas.Quota(60)]
        )

    counts = {'foo': 0 , 'bar': 0, 'zee': 0}
    for i in range(0, 1000):
        # Check the assembled result
        assembled = maker._assemble()
        assert assembled[0] in [0, 1, 2] and assembled[1] == None

        # Check the finished result
        finished = maker._finish(assembled)
        assert finished in ['foo', 'bar', 'zee']

        # Count the occurances
        counts[finished] += 1

    # Confirm the counts are as approx. evenly distributed
    assert int(round(counts['foo'] / 100)) == 1
    assert int(round(counts['bar'] / 100)) == 3
    assert int(round(counts['zee'] / 100)) == 6


def test_some_or():
    """
    `SomeOf` makers should return a list of values at random (optionally
    weighted) from a list of items (python types of or makers).
    """

    # Seed the random generator to ensure test results are consistent
    random.seed(110679)

    # @@ Configured to return a sample from a list of python types

    # @@ Configured to return a sample from a list of makers

    # @@ Configured to return a sample from a list of python types weighted

    # @@ Configured to return a sample from a list of python types with replacement

    # @@ Configured to return a sample from a list of python types weighted with
    # replacement.

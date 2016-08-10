import math
import random

from mongoframes.factory import makers
from mongoframes.factory import quotas
from mongoframes.factory.makers import selections as selection_makers
from mongoframes.queries import Q

from tests.fixtures import *


def test_cycle():
    """
    `Cycle` makers should return values from a list of items (python types of or
    makers) one after another.
    """

    # Configured to cycle through a list of python types
    maker = selection_makers.Cycle(['foo', 'bar', 'zee'])

    index = 0
    for value in ['foo', 'bar', 'zee', 'foo', 'bar']:

        # Check the assembled result
        assembled = maker._assemble()
        assert assembled == [index, None]

        # Check the finished result
        finished = maker._finish(assembled)
        assert finished == value

        # Track the index
        index += 1
        if index >= 3:
            index = 0

    # Configured to cycle throguh a list of makers
    maker = selection_makers.Cycle([
        makers.Static('foo'),
        makers.Static('bar'),
        makers.Static('zee')
        ])

    index = 0
    for value in ['foo', 'bar', 'zee', 'foo', 'bar']:

        # Check the assembled result
        assembled = maker._assemble()
        assert assembled == [index, value]

        # Check the finished result
        finished = maker._finish(assembled)
        assert finished == value

        # Track the index
        index += 1
        if index >= 3:
            index = 0

    # Reset should reset the cycle to the start
    maker.reset()

    # Check the assembled result
    assembled = maker._assemble()
    assert assembled == [0, 'foo']

    # Check the finished result
    finished = maker._finish(assembled)
    assert finished == 'foo'

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

    # Confirm the counts are approx. evenly distributed
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

    # Confirm the counts are approx. evenly distributed
    for value in ['foo', 'bar', 'zee']:
        assert int(round(counts[value] / 100)) == 3

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

    # Confirm the counts are approx. distributed based on the weights
    assert int(round(counts['foo'] / 100)) == 1
    assert int(round(counts['bar'] / 100)) == 3
    assert int(round(counts['zee'] / 100)) == 6

def test_random_reference(mongo_client, example_dataset_many):
    """
    `RandomReference` makers should return the Id of a document from from the
    specified `Frame`s collection at random.
    """

    # Seed the random generator to ensure test results are consistent
    random.seed(110679)

    # Configured without a constraint
    maker = selection_makers.RandomReference(ComplexDragon)

    # Check the assembled result
    assembled = maker._assemble()
    assert math.floor(assembled * 100) == 77

    # Check the finished result
    finished = maker._finish(assembled)
    assert finished == ComplexDragon.one(Q.name == 'Albert')._id

    # Configured with a constraint
    maker = selection_makers.RandomReference(ComplexDragon, Q.name != 'Albert')

    # Check the assembled result
    assembled = maker._assemble()
    assert math.floor(assembled * 100) == 78

    # Check the finished result
    finished = maker._finish(assembled)
    assert finished == ComplexDragon.one(Q.name == 'Fred')._id

def test_some_of():
    """
    `SomeOf` makers should return a list of values at random (optionally
    weighted) from a list of items (python types of or makers).
    """

    # Seed the random generator to ensure test results are consistent
    random.seed(110679)

    # Define the choices we'll be sampling from
    choices = ['foo', 'bar', 'zee', 'oof', 'rab', 'eez']
    choices_range = range(0, len(choices))
    choices_set = set(choices)

    # Configured to return a sample from a list of python types
    maker = selection_makers.SomeOf(list(choices), quotas.Quota(3))

    counts = {c: 0 for c in choices}
    for i in range(0, 1000):
        # Check the assembled result
        assembled = maker._assemble()
        assert len(assembled) == 3
        for item in assembled:
            assert item[0] in choices_range and item[1] == None

        # Check the finished result
        finished = maker._finish(assembled)
        assert len(set(finished)) == 3
        assert set(finished).issubset(choices_set)

        # Count occurances
        for value in finished:
            counts[value] += 1

    # Confirm the counts are approx. evenly distributed
    for value in choices:
        assert int(round(counts[value] / 100)) == 5

    # Configured to return a sample from a list of makers
    maker = selection_makers.SomeOf(
        [makers.Static(c) for c in choices],
        quotas.Quota(3)
        )

    counts = {c: 0 for c in choices}
    for i in range(0, 1000):
        # Check the assembled result
        assembled = maker._assemble()
        assert len(assembled) == 3
        for item in assembled:
            assert item[0] in choices_range and item[1] in choices

        # Check the finished result
        finished = maker._finish(assembled)
        assert len(set(finished)) == 3
        assert set(finished).issubset(choices_set)

        # Count occurances
        for value in finished:
            counts[value] += 1

    # Confirm the counts are approx. evenly distributed
    for value in choices:
        assert int(round(counts[value] / 100)) == 5

    # Configured to return a sample from a list of python types weighted
    maker = selection_makers.SomeOf(
        list(choices),
        quotas.Quota(3),
        weights=[1, 2, 4, 8, 16, 32]
        )

    counts = {c: 0 for c in choices}
    for i in range(0, 1000):
        # Check the assembled result
        assembled = maker._assemble()
        assert len(assembled) == 3
        for item in assembled:
            assert item[0] in choices_range and item[1] == None

        # Check the finished result
        finished = maker._finish(assembled)
        assert len(finished) == 3
        assert set(finished).issubset(choices_set)

        # Count occurances
        for value in finished:
            counts[value] += 1

    # Confirm the counts are approx. based on the weights
    for i, value in enumerate(choices):

        count = counts[value] / 1000
        prob = maker.p(i, 3, [1, 2, 4, 8, 16, 32])
        tol = prob * 0.15

        assert count > (prob - tol) and count < (prob + tol)

    # Configured to return a sample from a list of python types with replacement
    maker = selection_makers.SomeOf(
        [makers.Static(c) for c in choices],
        quotas.Quota(3),
        with_replacement=False
        )

    not_uniques = 0
    for i in range(0, 1000):
        # Check the assembled result
        assembled = maker._assemble()
        assert len(assembled) == 3
        for item in assembled:
            assert item[0] in choices_range and item[1] in choices

        # Check the finished result
        finished = maker._finish(assembled)
        assert len(finished) == 3
        assert set(finished).issubset(choices_set)

        # Count occurances of values with non-unique values
        if len(set(value)) < 3:
            not_uniques += 1

    # Check that some values where generated with non-unique items
    assert not_uniques > 0

    # Configured to return a sample from a list of python types weighted with
    # replacement.
    maker = selection_makers.SomeOf(
        list(choices),
        quotas.Quota(3),
        weights=[1, 2, 4, 8, 16, 32],
        with_replacement=True
        )

    counts = {c: 0 for c in choices}
    for i in range(0, 1000):
        # Check the assembled result
        assembled = maker._assemble()
        assert len(assembled) == 3
        for item in assembled:
            assert item[0] in choices_range and item[1] == None

        # Check the finished result
        finished = maker._finish(assembled)
        assert len(finished) == 3
        assert set(finished).issubset(choices_set)

        # Count occurances
        for value in finished:
            counts[value] += 1

    # Confirm the counts are approx. (+/- 15% tolerance) based on the weights
    weight = 1
    for value in choices:
        count = counts[value]
        prob = (weight / 63.0) * 3000.0
        tol = prob * 0.15

        assert count > (prob - tol) and count < (prob + tol)

        weight *= 2
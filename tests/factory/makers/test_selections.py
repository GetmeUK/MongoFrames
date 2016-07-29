from mongoframes.factory import makers
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

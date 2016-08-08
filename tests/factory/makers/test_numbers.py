from mongoframes.factory import quotas
from mongoframes.factory.makers import numbers as number_makers

from tests.fixtures import *


def test_counter():
    """`Counter` makers should return a number sequence"""

    # Configured with defaults
    maker = number_makers.Counter()

    for i in range(1, 100):
        # Check the assembled result
        assembled = maker._assemble()
        assert assembled == i

        # Check the finished result
        finished = maker._finish(assembled)
        assert finished == i

    # Configuered with custom start from and step
    maker = number_makers.Counter(quotas.Quota(10), quotas.Quota(5))

    for i in range(10, 100, 5):
        # Check the assembled result
        assembled = maker._assemble()
        assert assembled == i

        # Check the finished result
        finished = maker._finish(assembled)
        assert finished == i

    # Reset should reset the counter to the initial start from value
    maker.reset()

    # Check the assembled result
    assembled = maker._assemble()
    assert assembled == 10

    # Check the finished result
    finished = maker._finish(assembled)
    assert finished == 10

def test_float():
    "`Float` makers should return a float between two values"

    min_value = 2.5
    max_value = 7.2
    maker = number_makers.Float(min_value, max_value)

    for i in range(1, 100):
        # Check the assembled result
        assembled = maker._assemble()
        assert assembled >= min_value and assembled <= max_value

        # Check the finished result
        finished = maker._finish(assembled)
        assert finished >= min_value and assembled <= max_value

def test_int():
    "`Int` makers should return an integer between two values"

    min_value = 25
    max_value = 72
    maker = number_makers.Int(min_value, max_value)

    for i in range(1, 100):
        # Check the assembled result
        assembled = maker._assemble()
        assert assembled >= min_value and assembled <= max_value

        # Check the finished result
        finished = maker._finish(assembled)
        assert finished >= min_value and assembled <= max_value
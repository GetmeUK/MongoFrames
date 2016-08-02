from mongoframes.factory import quotas
from mongoframes.factory.makers import numbers as number_makers

from tests.fixtures import *


def test_counter():
    """`Counter` makers should return a number sequence"""

    # Configured with defaults
    maker = number_makers.Counter()

    # Check the assembled result
    for i in range(1, 100):
        assembled = maker._assemble()
        assert assembled == i

        # Check the finished result
        finished = maker._finish(assembled)
        assert finished == i

    # Configuered with custom start from and step
    maker = number_makers.Counter(quotas.Quota(10), quotas.Quota(5))

    # Check the assembled result
    for i in range(10, 100, 5):
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
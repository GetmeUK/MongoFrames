from mongoframes.factory import quotas
from mongoframes.factory.makers import numbers as number_makers

from tests.fixtures import *


def test_counter():
    """
    `Counter` makers should return a number sequence.
    """

    maker = number_makers.Counter(quotas.Quota(10), step=quotas.Quota(5))

    # Check the assembled result
    for i in range(10, 100, 5):
        assembled = maker._assemble()
        assert assembled == i

        # Check the finished result
        finished = maker._finish(assembled)
        assert finished == i
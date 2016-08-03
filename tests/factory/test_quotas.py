import math
import random

from mongoframes.factory import quotas


def test_quota():
    """
    The base `Quota` should convert to a quantity identical to the one it is
    initialized with.
    """

    quota = quotas.Quota(5)

    # Check quota converted to an integer
    assert int(quota) == 5

    # Check quota converted to a float
    assert float(quota) == 5.0

def test_gauss():
    """
    The `Gauss` quota should convert to a random quantity using a gaussian
    distribution and a given mean and standard deviation.
    """

    # Seed the random generator to ensure test results are consistent
    random.seed(110679)

    # Configure the quota
    std_dev = 0.1
    mean = 5
    quota = quotas.Gauss(mean, std_dev)

    # Count the number of times a value falls within each deviation
    std_devs = {1: 0, 2: 0, 3: 0}

    for i in range(0, 10000):
        qty = float(quota)

        # Calculate the deviation of the quantity from the mean
        dev = abs(qty - 5)

        # Tally the occurances within each deviation deviations
        if dev <= std_dev:
            std_devs[1] += 1

        if dev <= std_dev * 2:
            std_devs[2] += 1

        if dev <= std_dev * 3:
            std_devs[3] += 1

    # Check the deviations fall within the 68-95-99.7 rule
    assert math.ceil(std_devs[1] / 100) >= 68
    assert math.ceil(std_devs[2] / 100) >= 95
    assert math.ceil(std_devs[3] / 100) >= 99.7

def test_random():
    """
    The `Random` quota should convert to a random quantity between a minimum and
    maximum value.
    """

    min_qty = 5
    max_qty = 25
    quota = quotas.Random(min_qty, max_qty)

    for i in range(0, 1000):
        qty_int = int(quota)
        qty_float = float(quota)

        # Check the quantity falls between the given min/max range
        assert qty_int >= min_qty and qty_int <= max_qty
        assert qty_float >= min_qty and qty_float <= max_qty
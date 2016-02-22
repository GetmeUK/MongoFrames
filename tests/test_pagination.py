from pymongo import MongoClient
import pytest
from time import sleep
from unittest.mock import Mock

from mongoframes import *


# Classes

class Orc(Frame):
    """
    An orc.
    """

    _collection = 'Orc'
    _fields = {'name'}


@pytest.fixture(scope='function')
def example_dataset(request):
    """Connect to the database and create a set of example data (orcs)"""

    # Connect to mongodb and create a test database
    Frame._client = MongoClient('mongodb://localhost:27017/mongoframes_test')

    def fin():
        # Remove the test database
        Frame._client.drop_database('mongoframes_test')

    request.addfinalizer(fin)

    # Create 1,000 orcs
    for i in range(0, 1000):
        Orc(name='Orc {0:04d}'.format(i)).insert()

    return Frame._client


# Paginator tests

def test_paginator(example_dataset):
    """Paginate all orcs"""

    # Paginate all orcs
    paginator = Paginator(Orc)

    # Check the results are as expected
    assert paginator.item_count == 1000
    assert paginator.page_count == 50
    assert paginator.page_numbers == range(1, 51)

    i = 0
    for page in paginator:
        for orc in page:
            assert orc.name == 'Orc {0:04d}'.format(i)
            i += 1

def test_paginator_with_filter(example_dataset):
    """Paginate the last 100 orcs using a filter"""

    # Paginate all orcs
    paginator = Paginator(Orc, Q.name >= 'Orc 0900')

    # Check the results are as expected
    assert paginator.item_count == 100
    assert paginator.page_count == 5
    assert paginator.page_numbers == range(1, 6)

    i = 900
    for page in paginator:
        for orc in page:
            assert orc.name == 'Orc {0:04d}'.format(i)
            i += 1

def test_paginator_with_sort(example_dataset):
    """Paginate all orcs but sort them in reverse"""

    # Paginate all orcs
    paginator = Paginator(Orc, sort=[('name', DESC)])

    # Check the results are as expected
    assert paginator.item_count == 1000
    assert paginator.page_count == 50
    assert paginator.page_numbers == range(1, 51)

    i = 999
    for page in paginator:
        for orc in page:
            assert orc.name == 'Orc {0:04d}'.format(i)
            i -= 1

def test_paginator_with_projection(example_dataset):
    """Paginate all orcs but use a custom projection"""

    # Paginate all orcs
    paginator = Paginator(Orc, projection={'name': False})

    # Check the results are as expected
    assert paginator.item_count == 1000
    assert paginator.page_count == 50
    assert paginator.page_numbers == range(1, 51)

    for page in paginator:
        for orc in page:
            assert orc._id is not None
            assert orc.name is None

def test_paginator_with_per_page(example_dataset):

    # Paginate all orcs
    paginator = Paginator(Orc, per_page=100)

    # Check the results are as expected
    assert paginator.item_count == 1000
    assert paginator.page_count == 10
    assert paginator.page_numbers == range(1, 11)

    i = 0
    for page in paginator:
        for orc in page:
            assert orc.name == 'Orc {0:04d}'.format(i)
            i += 1

def test_paginator_with_orphans(example_dataset):

    # Paginate all orcs
    paginator = Paginator(Orc, Q.name >= 'Orc 0918', orphans=2)

    # Check the results are as expected
    assert paginator.item_count == 82
    assert paginator.page_count == 4
    assert paginator.page_numbers == range(1, 5)

    i = 918
    for page in paginator:
        for orc in page:
            assert orc.name == 'Orc {0:04d}'.format(i)
            i += 1

    # Check the last page has 22 items
    assert len(paginator[4]) == 22

# Page tests

# def test_page():

    # getitem
    # iter
    # len

# def test_page_items():
# def test_page_next():
# def test_page_number():
# def test_page_offset():
# def test_page_prev():
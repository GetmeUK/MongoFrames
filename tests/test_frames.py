from pymongo import MongoClient
import pytest

from mongoframes import *


# Classes

class Dragon(Frame):
    """
    A dragon.
    """

    _collection = 'Dragon'
    _fields = [
        'name',
        'breed'
        ]
    _private_fields = ['breed']


class Lair(Frame):
    """
    A lair in which a dragon resides.
    """

    _collection = 'Lair'
    _fields = [
        'name',
        'gold'
        ]


# Fixtures

@pytest.fixture(scope='function')
def mongo_client(request):
    # Connect to mongodb and create a test database
    Frame._client = MongoClient('mongodb://localhost:27017/mongoframes_test')

    def fin():
        # Remove the test database
        Frame._client.drop_database('mongoframes_test')

    request.addfinalizer(fin)

    return Frame._client


# Tests

def test_frame():
    """Should create a new Dragon instance"""

    # Passing no inital values
    burt = Dragon()
    assert isinstance(burt, Dragon)

    # Passing initial values
    burt = Dragon(
        name='Burt',
        breed='Cold-drake'
        )
    assert burt.name == 'Burt'
    assert burt.breed == 'Cold-drake'

def test_equal(mongo_client):
    """Should compare the equality of two Frame instances by Id"""

    # Create some dragons
    burt = Dragon(
        name='Burt',
        breed='Cold-drake'
        )
    burt.insert()

    fred = Dragon(
        name='Fred',
        breed='Fire-drake'
        )
    fred.insert()

    # Test equality
    assert burt != fred
    assert burt == burt

def test_sort(mongo_client):
    """Should sort a list of Frame instances by their Ids"""

    # Create some dragons
    burt = Dragon(
        name='Burt',
        breed='Cold-drake'
        )
    burt.insert()

    fred = Dragon(
        name='Fred',
        breed='Fire-drake'
        )
    fred.insert()

    albert = Dragon(
        name='Albert',
        breed='Stone dragon'
        )
    albert.insert()

    # Test sorting by Id
    assert sorted([albert, burt, fred]) == [burt, fred, albert]

def test_to_json_type(mongo_client):
    """
    Should return a dictionary for the document with all values converted to
    JSON safe types. All private fields should be excluded.
    """

    # Create a dragon
    class ComplexDragon(Dragon):

        _fields = Dragon._fields + [
            'lair'
            ]

    # @@ Date
    # @@ Datetime
    # @@ ObjectId
    # @@ Frame
    # @@ List
    # @@ Dictionary
    # @@ SubFrame

    cave = Lair(
        name='Cave',
        gold=100
        )
    cave.insert()

    burt = ComplexDragon(
        name='Burt',
        breed='Cold-drake',
        lair=cave
        )
    burt.insert()

    assert burt.to_json_type() == {
        '_id': str(burt._id),
        'name': 'Burt',
        'lair': {
            '_id': str(cave._id),
            'name': 'Cave',
            'gold': 100
            }
        }

def test_insert(mongo_client):
    """Should insert a record into the database"""

    # Create a dragon
    burt = Dragon(
        name='Burt',
        breed='Cold-drake'
        )
    burt.insert()

    # Test the document now has an Id
    assert burt._id is not None

    # Get the document from the database and check it's values
    burt = Dragon.one(Q._id == burt._id)

    assert burt.name == 'Burt'
    assert burt.breed == 'Cold-drake'



# def __getattr__(self, name):
# def __setattr__(self, name, value):

# Operations
# def insert(self):
# def update(self):
# def delete(self):
# def insert_many(cls, documents):
# def update_many(cls, documents):
# def delete_many(cls, documents):

# Querying
# def count(cls, filter=None, **kwargs):
# def one(cls, filter, **kwargs):
# def many(cls, filter=None, **kwargs):

# Integrity helpers
# def timestamp_insert(sender, documents=[]):
# def timestamp_update(sender, documents=[]):
# def cascade(cls, field, documents):
# def nullify(cls, field, documents):
# def pull(cls, field, documents):

# Signals
# def listen(cls, event, func):
# def stop_listening(cls, event, func):

# Misc.
# def get_collection(cls):
# def get_db(cls):
# def get_fields(cls):
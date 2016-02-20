from datetime import datetime
from pymongo import MongoClient
import pytest

from mongoframes import *


# Classes

class Dragon(Frame):
    """
    A dragon.
    """

    _collection = 'Dragon'
    _fields = {
        'name',
        'breed'
        }
    _private_fields = {'breed'}


class Inventory(SubFrame):
    """
    An inventory of items kept within a lair.
    """

    _fields = {
        'gold',
        'skulls'
        }
    _private_fields = {'gold'}


class Lair(Frame):
    """
    A lair in which a dragon resides.
    """

    _collection = 'Lair'
    _fields = {
        'name',
        'inventory'
        }


class ComplexDragon(Dragon):

    _fields = Dragon._fields | {
        'dob',
        'lair',
        'traits'
        }

    _default_projection = {
        'lair': {
            '$ref': Lair,
            'inventory': {'$sub': Inventory}
            }
        }



# Fixtures

@pytest.fixture(scope='function')
def mongo_client(request):
    """Connect to the test database"""

    # Connect to mongodb and create a test database
    Frame._client = MongoClient('mongodb://localhost:27017/mongoframes_test')

    def fin():
        # Remove the test database
        Frame._client.drop_database('mongoframes_test')

    request.addfinalizer(fin)

    return Frame._client

@pytest.fixture(scope='function')
def example_dataset(request):
    """Create an example set of data that can be used in testing"""
    inventory = Inventory(
        gold=1000,
        skulls=100
        )

    cave = Lair(
        name='Cave',
        inventory=inventory
        )
    cave.insert()

    burt = ComplexDragon(
        name='Burt',
        dob=datetime(1979, 6, 11),
        breed='Cold-drake',
        lair=cave,
        traits=['irritable', 'narcissistic']
        )
    burt.insert()


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

def test_dot_notation():
    """
    @@ Should allow access to read and set document values using do notation.
    """
    assert False

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

def test_to_json_type(mongo_client, example_dataset):
    """
    Should return a dictionary for the document with all values converted to
    JSON safe types. All private fields should be excluded.
    """

    burt = ComplexDragon.one(Q.name == 'Burt')
    cave = burt.lair

    assert burt.to_json_type() == {
        '_id': str(burt._id),
        'name': 'Burt',
        'dob': '1979-06-11 00:00:00',
        'traits': ['irritable', 'narcissistic'],
        'lair': {
            '_id': str(cave._id),
            'name': 'Cave',
            'inventory': {
                'skulls': 100
                }
            }
        }

def test_insert(mongo_client):
    """@@ Should insert a document into the database"""

    # Create some convoluted data to insert
    inventory = Inventory(
        gold=1000,
        skulls=100
        )

    cave = Lair(
        name='Cave',
        inventory=inventory
        )
    cave.insert()

    burt = ComplexDragon(
        name='Burt',
        dob=datetime(1979, 6, 11),
        breed='Cold-drake',
        lair=cave,
        traits=['irritable', 'narcissistic']
        )
    burt.insert()

    burt = ComplexDragon.one(Q.name == 'Burt')

    # Test the document now has an Id
    assert burt._id is not None

    # Get the document from the database and check it's values
    burt.reload()

    assert burt.name == 'Burt'
    assert burt.breed == 'Cold-drake'
    assert False

def test_update(mongo_client):
    """@@ Should update a document on the database"""

    burt = Dragon(
        name='Burt',
        breed='Cold-drake'
        )
    burt.insert()

    burt = Dragon.one(Q._id == burt._id)

    burt.breed = 'Fire-drake'
    burt.update('breed')

    burt.reload()

    assert burt.name == 'Burt'
    assert burt.breed == 'Fire-drake'
    assert False

def test_upsert(mongo_client):
    """
    @@ Should update or insert a document on the database depending on whether
    or not it already exists.
    """
    assert False

def test_delete(mongo_client):
    """@@ Should delete a document from the database"""
    assert False

def test_insert_many(mongo_client):
    """@@ Should insert multiple documents records into the database"""
    assert False

def test_update_many(mongo_client):
    """@@ Should update mulitple documents on the database"""
    assert False

def test_delete_many(mongo_client):
    """@@ Should delete mulitple documents from the database"""
    assert False

def test_reload(mongo_client):
    """@@ Should reload the current document's values from the database"""
    assert False

def test_by_id(mongo_client):
    """@@ Should return a document by Id from the database"""
    assert False

def test_by_id(mongo_client):
    """@@ Should return a document by it's Id from the database"""
    assert False

def test_by_count(mongo_client):
    """@@ Should return a count for documents matching the given query"""
    assert False

def test_one(mongo_client):
    """@@ Should return a the first document that matches the given query"""
    assert False

def test_many(mongo_client):
    """@@ Should return all documents that match the given query"""
    assert False

def test_timestamp_insert(mongo_client):
    """
    @@ Should assign a timestamp to the `created` and `modified` field for a
    document.
    """
    assert False

def test_timestamp_update(mongo_client):
    """@@ Should assign a timestamp to the `modified` field for a document"""
    assert False

def test_cascade(mongo_client):
    """@@ Should apply a cascading delete"""
    assert False

def test_nullify(mongo_client):
    """@@ Should nullify a reference field"""
    assert False

def test_pull(mongo_client):
    """@@ Should pull references from a list field"""
    assert False

def test_listen(mongo_client):
    """@@ Should add a callback for a signal against the class"""
    assert False

def test_stop_listening(mongo_client):
    """@@ Should remove a callback for a signal against the class"""
    assert False

def test_get_collection(mongo_client):
    """@@ Return a reference to the database collection for the class"""
    assert False

def test_get_db(mongo_client):
    """@@ Return the database for the collection"""
    assert False
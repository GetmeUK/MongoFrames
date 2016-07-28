from datetime import datetime

from pymongo import MongoClient
import pytest

from mongoframes import *

__all__ = [
    # Frames
    'Dragon',
    'Inventory',
    'Lair',
    'ComplexDragon',
    'MonitoredDragon',

    # Fixtures
    'mongo_client',
    'example_dataset_one',
    'example_dataset_many'
    ]


# Classes

class Dragon(Frame):
    """
    A dragon.
    """

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

    _fields = {
        'name',
        'inventory'
        }


class ComplexDragon(Dragon):

    _fields = Dragon._fields | {
        'dob',
        'lair',
        'traits',
        'misc'
        }

    _default_projection = {
        'lair': {
            '$ref': Lair,
            'inventory': {'$sub': Inventory}
            }
        }

class MonitoredDragon(Dragon):

    _fields = Dragon._fields | {
        'created',
        'modified'
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
def example_dataset_one(request):
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

@pytest.fixture(scope='function')
def example_dataset_many(request):
    """Create an example set of data that can be used in testing"""

    # Burt
    cave = Lair(
        name='Cave',
        inventory=Inventory(
            gold=1000,
            skulls=100
            )
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

    # Fred
    castle = Lair(
        name='Castle',
        inventory=Inventory(
            gold=2000,
            skulls=200
            )
        )
    castle.insert()

    fred = ComplexDragon(
        name='Fred',
        dob=datetime(1980, 7, 12),
        breed='Fire-drake',
        lair=castle,
        traits=['impulsive', 'loyal']
        )
    fred.insert()

    # Fred
    mountain = Lair(
        name='Mountain',
        inventory=Inventory(
            gold=3000,
            skulls=300
            )
        )
    mountain.insert()

    albert = ComplexDragon(
        name='Albert',
        dob=datetime(1981, 8, 13),
        breed='Stone dragon',
        lair=mountain,
        traits=['reclusive', 'cunning']
        )
    albert.insert()
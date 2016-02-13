from mongoframes.frames import Frame
from mongoframes.queries import *


class Dragon(Frame):
    """
    A dragon.
    """

    _collection = 'Dragon'
    _fields = [
        'created',
        'modified',
        'name',
        'breed'
        ]


Dragon.listen('insert', Dragon.timestamp_insert)
Dragon.listen('update', Dragon.timestamp_update)



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
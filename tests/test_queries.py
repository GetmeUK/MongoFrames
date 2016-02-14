from mongoframes import *


def test_q():
    """Should generate a field path"""

    # Single
    assert Q.foo._path == 'foo'

    # Path
    assert Q.foo.bar._path == 'foo.bar'

    # Path with index
    assert Q.foo.bar[2]._path == 'foo.bar.2'

    # Path with `_path` using item getter
    assert Q.foo.bar[2]['_path']._path == 'foo.bar.2._path'


# Conditions as operator overrides

def test_equal():
    """Should generate an equals condition"""
    assert (Q.foo == 123).to_dict() == {'foo': 123}

def test_greater_than_or_equal():
    """Should generate a greater than or equal condition"""
    assert (Q.foo >= 123).to_dict() == {'foo': {'$gte': 123}}

def test_greater_than():
    """Should generate a greater than condition"""
    assert (Q.foo > 123).to_dict() == {'foo': {'$gt': 123}}

def test_less_than_or_equal():
    """Should generate a less than or equal condition"""
    assert (Q.foo <= 123).to_dict() == {'foo': {'$lte': 123}}

def test_less_than():
    """Should generate a less than condition"""
    assert (Q.foo < 123).to_dict() == {'foo': {'$lt': 123}}

def test_not_equal():
    """Should generate a not equals condition"""
    assert (Q.foo != 123).to_dict() == {'foo': {'$ne': 123}}


# Conditions through functions

def test_all():
    """Should generate a contains all values condition"""
    assert All(Q.foo, [1, 2, 3]).to_dict() == {'foo': {'$all': [1, 2, 3]}}

def test_exists():
    """Should generate an exists test condition"""
    assert Exists(Q.foo, True).to_dict() == {'foo': {'$exists': True}}

def test_in():
    """Should generate a contains condition"""
    assert In(Q.foo, [1, 2, 3]).to_dict() == {'foo': {'$in': [1, 2, 3]}}

def test_not():
    """Should generate a logical not condition"""
    assert Not(Q.foo == 123).to_dict() == {'foo': {'$not': {'$eq': 123}}}

def test_not_in():
    """Should generate a does not contain condition"""
    assert NotIn(Q.foo, [1, 2, 3]).to_dict() == {'foo': {'$nin': [1, 2, 3]}}

def test_size():
    """Should generate a array value size matches condition"""
    assert Size(Q.foo, 2).to_dict() == {'foo': {'$size': 2}}

def test_type():
    """Should generate a equals instance of condition"""
    assert Type(Q.foo, 'string').to_dict() == {'foo': {'$type': 'string'}}


# Groups

def test_and():
    """Should group one or more conditions by a logical and"""
    assert And(Q.foo == 123, Q.bar != 456).to_dict() == \
        {'$and': [{'foo': 123}, {'bar': {'$ne': 456}}]}

def test_or():
    """Should group one or more conditions by a logical or"""
    assert Or(Q.foo == 123, Q.bar != 456).to_dict() == \
        {'$or': [{'foo': 123}, {'bar': {'$ne': 456}}]}

def test_nor():
    """Should group one or more conditions by a logical nor"""
    assert Nor(Q.foo == 123, Q.bar != 456).to_dict() == \
        {'$nor': [{'foo': 123}, {'bar': {'$ne': 456}}]}


# Utils

def test_to_refs():
    """Should convert all Frame instances within a value to Ids"""

    # Convert a single Frame instance
    assert to_refs(Frame(_id=1)) == 1

    # Convert a list of Frame instances
    assert to_refs([Frame(_id=1), Frame(_id=2)]) == [1, 2]

    # Convert a dictionary of Frame instances
    assert to_refs({1: Frame(_id=1), 2: Frame(_id=2)}) == {1: 1, 2: 2}

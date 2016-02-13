"""
A set of helpers to simplify the creation of mongo queries.
"""


__all__ = [
    # Queries
    'Q',

    # Operators
    'All',
    'Exists',
    'In',
    'Not',
    'NotIn',
    'Size',
    'Type',

    # Groups
    'And',
    'Or',
    'Nor',

    # Utils
    'to_refs'
    ]


# Queries

class Condition:
    """
    A query condition of the form `{path: {operator: value}}`.
    """

    def __init__(self, q, value, operator):
        self.q = q
        self.value = value
        self.operator = operator

    def to_dict(self):
        if self.operator == '$eq':
            return {self.q: self.value}
        return {self.q: {self.operator: self.value}}


class QMeta(type):
    """
    Meta-class for query builder.
    """

    def __getattr__(self, name):
        return Q(name)

    def __getitem__(self, name):
        return Q(name)


class Q(metaclass=QMeta):
    """
    Start point for query creation.
    """

    def __init__(self, path):
        self._path = path

    def __eq__(self, other):
        return Condition(self._path, other, '$eq')

    def __ge__(self, other):
        return Condition(self._path, other, '$gte')

    def __gt__(self, other):
        return Condition(self._path, other, '$gt')

    def __le__(self, other):
        return Condition(self._path, other, '$lte')

    def __lt__(self, other):
        return Condition(self._path, other, '$lt')

    def __ne__(self, other):
        return Condition(self._path, other, '$ne')

    def __getattr__(self, name):
        self._path = '{0}.{1}'.format(self._path, name)
        return self

    def __getitem__(self, name):
        self._path = '{0}.{1}'.format(self._path, name)
        return self


# Operators

def All(q, value):
    return Condition(q._path, to_refs(value), '$all')

def Exists(q, value):
    return Condition(q._path, value, '$exists')

def In(q, value):
    return Condition(q._path, to_refs(value), '$in')

def Not(condition):
    return Condition(
        condition.q,
        {condition.operator: condition.value},
        '$not'
        )

def NotIn(q, value):
    return Condition(q._path, to_refs(value), '$nin')

def Size(q, value):
    return Condition(q._path, value, '$size')

def Type(q, value):
    return Condition(q._path, value, '$type')


# Groups

class Group:
    """Base class for groups"""

    operator = ''

    def __init__(self, *conditions):
        self.conditions = conditions

    def to_dict(self):
        raw_conditions = []
        for condition in self.conditions:
            if hasattr(condition, 'to_dict'):
                raw_conditions.append(condition.to_dict())
            else:
                raw_conditions.append(condition)
        return {self.operator: raw_conditions}


class And(Group):

    operator = '$and'


class Or(Group):

    operator = '$or'


class Nor(Group):

    operator = '$nor'


# Utils

def to_refs(value):
    """Convert all Frame instances within the given value to Ids"""
    from .frames import Frame

    # Frame
    if isinstance(value, Frame):
        return value._id

    # Lists
    elif isinstance(value, (list, tuple)):
        return [to_refs(v) for v in value]

    # Dictionaries
    elif isinstance(value, dict):
        return {k: to_refs(v) for k, v in value.items()}

    return value
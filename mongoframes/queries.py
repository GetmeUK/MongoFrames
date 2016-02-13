"""
A set of helpers to simplify the creation of mongo queries.
"""

from . import Frame


__all__ = [
    # Queries
    'Q',

    # Groups
    'And',
    'Or',
    'Nor',

    # Operators
    'All',
    'Exists',
    'In',
    'Not',
    'NotIn',
    'Size',
    'Type'
    ]


# Queries

class Condition:
    """
    A query condition of the form `{field: {operator: value}}`.
    """

    def __init__(self, field, value, operator):
        self.field = field
        self.value = value
        self.operator = operator

    def to_pymongo(self):
        if self.operator == '$eq':
            return {self.field: self.value}

        return {self.field: {self.operator: Frame._pymongo_safe(self.value)}}


class Field:
    """
    A document field within a query.
    """

    def __init__(self, key):
        self.key = key

    def __eq__(self, other):
        return Condition(self.key, other, '$eq')

    def __ge__(self, other):
        return Condition(self.key, other, '$gte')

    def __gt__(self, other):
        return Condition(self.key, other, '$gt')

    def __le__(self, other):
        return Condition(self.key, other, '$lte')

    def __lt__(self, other):
        return Condition(self.key, other, '$lt')

    def __ne__(self, other):
        return Condition(self.key, other, '$ne')

    def __iadd__(self, other):
        return Condition(self.key, other, '$in')

    def __isub__(self, other):
        return Condition(self.key, other, '$nin')

    def __getattr__(self, name):
        self.key = '{0}.{1}'.format(self.key, name)
        return self


class QMeta(type):
    """
    Meta-class for query builder.
    """

    def __getattr__(self, name):
        return Field(name)

    def __getitem__(self, name):
        return Field(name)


class Q(metaclass=QMeta):
    """
    A class for starting and building queries, for example:

    query = Q.name == 'Steve Wozniak'

    ...will convert to...

    {name: 'Steve Wozniak'}
    """


# Groups

class Group:
    """Base class for groups"""

    operator = ''

    def __init__(self, *conditions):
        self.conditions = conditions

    def to_pymongo(self):
        raw_conditions = []
        for condition in self.conditions:
            if hasattr(condition, 'to_pymongo'):
                raw_conditions.append(condition.to_pymongo())
            else:
                raw_conditions.append(condition)
        return {self.operator: raw_conditions}


class And(Group):

    operator = '$and'


class Or(Group):

    operator = '$or'


class Nor(Group):

    operator = '$nor'


# Operators

def All(field, value):
    return Condition(field.key, Frame._pymongo_safe(value), '$all')

def Exists(field, value):
    return Condition(field.key, value, '$exists')

def In(field, value):
    return Condition(field.key, Frame._pymongo_safe(value), '$in')

def Not(condition):
    if condition.operator == '$eq':
        return Condition(condition.field, condition.value, '$not')

    return Condition(
        condition.field,
        {condition.operator: condition.value},
        '$not'
        )

def NotIn(field, value):
    return Condition(field.key, Frame._pymongo_safe(value), '$nin')

def Size(field, value):
    return Condition(field.key, value, '$size')

def Type(field, value):
    return Condition(field.key, value, '$type')
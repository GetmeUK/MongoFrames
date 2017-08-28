"""
A set of helpers to simplify the creation of MongoDB queries.
"""

import re

from pymongo import (ASCENDING, DESCENDING)

__all__ = [
    # Queries
    'Q',

    # Operators
    'All',
    'ElemMatch',
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

    # Sorting
    'SortBy',

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
        """Return a dictionary suitable for use with pymongo as a filter"""
        if self.operator == '$eq':
            return {self.q: self.value}
        if self.q is None:
            return {self.operator: self.value}
        return {self.q: {self.operator: self.value}}


class QMeta(type):
    """
    Meta-class for query builder.
    """

    def __getattr__(self, name):
        return Q(name)

    def __getitem__(self, name):
        return Q(name)

    def __eq__(self, other):
        return Condition(None, other, '$eq')

    def __ge__(self, other):
        return Condition(None, other, '$gte')

    def __gt__(self, other):
        return Condition(None, other, '$gt')

    def __le__(self, other):
        return Condition(None, other, '$lte')

    def __lt__(self, other):
        return Condition(None, other, '$lt')

    def __ne__(self, other):
        return Condition(None, other, '$ne')


class Q(metaclass=QMeta):
    """
    Start point for the query creation, the Q class is a special type of class
    that's typically initialized by appending an attribute, for example:

        Q.hit_points > 100

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
    """
    The All operator selects documents where the value of the field is an list
    that contains all the specified elements.
    """
    return Condition(q._path, to_refs(value), '$all')

def ElemMatch(q, *conditions):
    """
    The ElemMatch operator matches documents that contain an array field with at
    least one element that matches all the specified query criteria.
    """
    new_condition = {}
    for condition in conditions:
        deep_merge(condition.to_dict(), new_condition)

    return Condition(q._path, new_condition, '$elemMatch')

def Exists(q, value):
    """
    When exists is True, Exists matches the documents that contain the field,
    including documents where the field value is null. If exists is False, the
    query returns only the documents that do not contain the field.
    """
    return Condition(q._path, value, '$exists')

def In(q, value):
    """
    The In operator selects the documents where the value of a field equals any
    value in the specified list.
    """
    return Condition(q._path, to_refs(value), '$in')

def Not(condition):
    """
    Not performs a logical NOT operation on the specified condition and selects
    the documents that do not match. This includes documents that do not contain
    the field.
    """
    return Condition(
        condition.q,
        {condition.operator: condition.value},
        '$not'
        )

def NotIn(q, value):
    """
    The NotIn operator selects documents where the field value is not in the
    specified list or the field does not exists.
    """
    return Condition(q._path, to_refs(value), '$nin')

def Size(q, value):
    """
    The Size operator matches any list with the number of elements specified by
    size.
    """
    return Condition(q._path, value, '$size')

def Type(q, value):
    """
    Type selects documents where the value of the field is an instance of the
    specified BSON type.
    """
    return Condition(q._path, value, '$type')


# Groups

class Group:
    """
    The Group class is used as a base class for operators that group together
    two or more conditions.
    """

    operator = ''

    def __init__(self, *conditions):
        self.conditions = conditions

    def to_dict(self):
        """Return a dictionary suitable for use with pymongo as a filter"""
        raw_conditions = []
        for condition in self.conditions:
            if isinstance(condition, (Condition, Group)):
                raw_conditions.append(condition.to_dict())
            else:
                raw_conditions.append(condition)
        return {self.operator: raw_conditions}


class And(Group):
    """
    And performs a logical AND operation on a list of two or more conditions and
    selects the documents that satisfy all the conditions.
    """

    operator = '$and'


class Or(Group):
    """
    The Or operator performs a logical OR operation on a list of two or more
    conditions and selects the documents that satisfy at least one of the
    conditions.
    """

    operator = '$or'


class Nor(Group):
    """
    Nor performs a logical NOR operation on a list of one or more conditions and
    selects the documents that fail all the conditions.
    """

    operator = '$nor'


# Sorting

def SortBy(*qs):
    """Convert a list of Q objects into list of sort instructions"""

    sort = []
    for q in qs:
        if q._path.endswith('.desc'):
            sort.append((q._path[:-5], DESCENDING))
        else:
            sort.append((q._path, ASCENDING))
    return sort


# Utils

def deep_merge(source, dest):
    """
    Deep merges source dict into dest dict.

    This code was taken directly from the mongothon project:
    https://github.com/gamechanger/mongothon/tree/master/mongothon
    """
    for key, value in source.items():
        if key in dest:
            if isinstance(value, dict) and isinstance(dest[key], dict):
                deep_merge(value, dest[key])
                continue
            elif isinstance(value, list) and isinstance(dest[key], list):
                for item in value:
                    if item not in dest[key]:
                        dest[key].append(item)
                continue
        dest[key] = value

def to_refs(value):
    """Convert all Frame instances within the given value to Ids"""
    from mongoframes.frames import Frame, SubFrame

    # Frame
    if isinstance(value, Frame):
        return value._id

    # SubFrame
    elif isinstance(value, SubFrame):
        return to_refs(value._document)

    # Lists
    elif isinstance(value, (list, tuple)):
        return [to_refs(v) for v in value]

    # Dictionaries
    elif isinstance(value, dict):
        return {k: to_refs(v) for k, v in value.items()}

    return value
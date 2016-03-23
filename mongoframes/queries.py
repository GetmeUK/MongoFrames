"""
A set of helpers to simplify the creation of mongodb queries.
"""


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

def ElemMatch(q, *value):
    # Support for a list of conditions being specified for an element match
    new_value = {}
    for condition in value:
        deep_merge(condition.to_dict(), new_value)

    return Condition(q._path, new_value, '$elemMatch')

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
            if isinstance(condition, (Condition, Group)):
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
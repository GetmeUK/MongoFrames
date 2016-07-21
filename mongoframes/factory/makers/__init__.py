import random

import faker

from mongoframes.queries import Q

__all__ = [
    'Faker',
    'Lambda',
    'ListOf',
    'Reference',
    'Static',
    'SubFactory',
    'Unique'
    ]


class Maker:
    """
    A base class for all Maker classes.
    """

    def __call__(self, *args):
        if args:
            return self._finish(*args)
        return self._assemble()

    def reset(self):
        """Reset the maker instance"""
        pass

    def _assemble(self):
        return None

    def _finish(self, value):
        return value

    @staticmethod
    def get_fake():
        """Return a shared faker factory used to generate fake data"""
        if not hasattr(Maker, '_fake'):
            Maker._fake = faker.Factory.create()
        return Maker._fake


class Faker(Maker):
    """
    Use any faker provider to generate a value (see
    http://fake-factory.readthedocs.io/)
    """

    def __init__(self, provider, assembler=True, **kwargs):

        # The provider that will be used to generate the value
        self._provider = provider

        # Flag indicating if the providers should be called in _assemble (True)
        # or _finish (False).
        self._assembler = assembler

        # The keyword arguments for the provider
        self._kwargs = kwargs

    def _assemble(self):
        if not self._assembler:
            return None
        return getattr(self.get_fake(), self._provider)(**self._kwargs)

    def _finish(self, value):
        if self._assembler:
            return value
        return getattr(self.get_fake(), self._provider)(**self._kwargs)


class Lambda(Maker):
    """
    Use a lambda function to generate a value.
    """

    def __init__(self, func, assembler=True):

        # The function to call
        self._func = func

        # Flag indicating if the lambda function should be called in _assemble
        # (True) or _finish (False).
        self._assembler = assembler

    def _assemble(self):
        if self._assembler:
            return self._func()
        return None

    def _finish(self, value):
        if self._assembler:
            return value
        return self._func()


class ListOf(Maker):
    """
    Make a list of values using another maker to generate each value.
    """

    def __init__(self, maker, quantity):

        # The maker used to generate each value in the list
        self._maker = maker

        # The number of list items to generate
        self._quantity = quantity

    def _assemble(self):
        quantity = int(self._quantity)
        return [self._maker() for i in range(0, quantity)]

    def _finish(self, value):
        return [self._maker(v) for v in value]


class Reference(Maker):
    """
    Make a reference to another document.
    """

    def __init__(self, frame_cls, field_name, values):

        # The `Frame` class that will be used to obtain the referenced document
        self._frame_cls = frame_cls

        # The field name that will be used to query for the referenced document
        self._field_name = field_name

        # The list of values that can be used to select a reference
        self._values = values

    def _assemble(self):
        return random.choice(self._values)

    def _finish(self, value):
        return self._frame_cls.one(Q[self._field_name] == value)


class Static(Maker):
    """
    A maker that returns a fixed given value.
    """

    def __init__(self, value, assembler=True):

        # The value to return
        self._value = value

        # Flag indicating if the value should be return in _assemble (True) or
        # _finish (False).
        self._assembler = assembler

    def _assemble(self):
        if self._assembler:
            return self._value
        return None

    def _finish(self, value):
        if self._assembler:
            return value
        return self._value

class SubFactory(Maker):
    """
    A maker that makes sub-documents.
    """

    def __init__(self, blueprint, presets=None):

        # The blueprint to produce
        self._blueprint = blueprint

        # A list of presets to apply with the blueprint
        self._presets = presets or []

    def reset(self):
        """Reset the associated blueprint and presets"""
        self._blueprint.reset(self._presets)

    def _assemble(self):
        return self._blueprint.assemble(self._presets)

    def _finish(self, value):
        return self._blueprint.finish(value, self._presets)


class Unique(Maker):
    """
    Ensure that unique values are generated.
    """

    def __init__(self,
        maker,
        existing_values=None,
        assembler=False,
        max_attempts=1000
        ):

        # The maker that will generate values
        self._maker = maker

        # A set of existing values
        self._existing_values = existing_values or set([])

        # Flag indicating if the providers should be called in _assemble (True)
        # or _finish (False).
        self._assembler = assembler

        # A set of used values
        self._used_values = set(self._existing_values)

        # The maximum number of attempts to generate unique data that should be
        # performed.
        self._max_attempts = max_attempts

    def reset(self):
        """Reset the set of used values"""
        self._used_values = set(self._existing_values)

    def _get_unique(self, *args):
        """Generate a unique value using the assigned maker"""

        # Generate a unique values
        value = ''
        attempts = 0
        while True:
            attempts += 1
            value = self._maker(*args)
            if value not in self._used_values:
                break

            assert attempts < self._max_attempts, \
                'Too many attempts to generate a unique value'

        # Add the value to the set of used values
        self._used_values.add(value)

        return value

    def _assemble(self):
        if not self._assembler:
            return self._maker()

    def _finish(self, value):
        if self._assembler:
            return self.maker(value)

        return self._get_unique(value)
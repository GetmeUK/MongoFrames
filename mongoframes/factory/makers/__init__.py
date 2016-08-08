import random

import faker

from mongoframes.queries import Q

__all__ = [
    'DictOf',
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


class DictOf(Maker):
    """
    Make a dictionary of key/values where each value is a set value or generated
    using a maker.
    """

    def __init__(self, table):

        # The table of keyword arguments that will be used to generate the
        # dictionary.
        self._table = table

    def _assemble(self):
        table = {}
        for k, v in self._table.items():
            if isinstance(v, Maker):
                table[k] = v._assemble()
            else:
                table[k] = None
        return table

    def _finish(self, value):
        table = {}
        for k, v in self._table.items():
            if isinstance(v, Maker):
                table[k] = self._table[k]._finish(value[k])
            else:
                table[k] = self._table[k]

        return table


class Faker(Maker):
    """
    Use any faker provider to generate a value (see
    http://fake-factory.readthedocs.io/)
    """

    default_locale = 'en_US'

    def __init__(self, provider, assembler=True, locale=None, **kwargs):

        # The provider that will be used to generate the value
        self._provider = provider

        # Flag indicating if the providers should be called in _assemble (True)
        # or _finish (False).
        self._assembler = assembler

        # The locale that will be used by the faker factory
        self._locale = locale or self.default_locale

        # The keyword arguments for the provider
        self._kwargs = kwargs

    def _assemble(self):
        if not self._assembler:
            return None
        provider = getattr(self.get_fake(self._locale), self._provider)
        return provider(**self._kwargs)

    def _finish(self, value):
        if self._assembler:
            return value
        provider = getattr(self.get_fake(self._locale), self._provider)
        return provider(**self._kwargs)

    @staticmethod
    def get_fake(locale=None):
        """Return a shared faker factory used to generate fake data"""
        if locale is None:
            locale = Faker.default_locale

        if not hasattr(Maker, '_fake_' + locale):
            Faker._fake = faker.Factory.create(locale)
        return Faker._fake


class Lambda(Maker):
    """
    Use a function to generate a value.
    """

    def __init__(self, func, assembler=True, finisher=False):

        assert assembler or finisher, \
                'Either `assembler` or `finisher` must be true for lambda'

        # The function to call
        self._func = func

        # Flag indicating if the lambda function should be called in _assemble
        self._assembler = assembler

        # Flag indicating if the lambda function should be called in _finish
        self._finisher = finisher

    def _assemble(self):
        if self._assembler:
            return self._func()
        return None

    def _finish(self, value):
        if self._finisher:
            return self._func(value)
        return value


class ListOf(Maker):
    """
    Make a list of values using another maker to generate each value.
    """

    def __init__(self, maker, quantity, reset_maker=False):

        # The maker used to generate each value in the list
        self._maker = maker

        # The number of list items to generate
        self._quantity = quantity

        # A flag indicating if the maker should be reset each time the list is
        # generated.
        self._reset_maker = reset_maker

    def _assemble(self):
        quantity = int(self._quantity)

        if self._reset_maker:
            self._maker.reset()

        return [self._maker() for i in range(0, quantity)]

    def _finish(self, value):

        if self._reset_maker:
            self._maker.reset()

        return [self._maker(v) for v in value]


class Reference(Maker):
    """
    Make a reference to another document.
    """

    def __init__(self, frame_cls, field_name, value):

        # The `Frame` class that will be used to obtain the referenced document
        self._frame_cls = frame_cls

        # The field name that will be used to query for the referenced document
        self._field_name = field_name

        # The list of values that can be used to select a reference
        self._value = value

    def _assemble(self):
        if isinstance(self._value, Maker):
            return self._value()
        return None

    def _finish(self, value):
        if isinstance(self._value, Maker):
            value = self._value(value)
        else:
            value = self._value

        # Convert the value to a reference
        value = self._frame_cls.one(
            Q[self._field_name] == value,
            projection={'_id': True}
            )

        # Check the referenced document was found
        if value:
            return value._id

        return None


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
        [frame_document, meta_document] = self._blueprint.finish(
            value,
            self._presets
            )

        # Initialize the sub-frame
        sub_frame = self._blueprint.get_frame_cls()(frame_document)

        # Apply any meta fields
        for key, value in meta_document.items():
            setattr(sub_frame, key, value)

        return sub_frame


class Unique(Maker):
    """
    Ensure that unique values are generated.
    """

    def __init__(self,
        maker,
        exclude=None,
        assembler=True,
        max_attempts=1000
        ):

        # The maker that will generate values
        self._maker = maker

        # A set of existing values
        self._exclude = exclude or set([])

        # Flag indicating if the providers should be called in _assemble (True)
        # or _finish (False).
        self._assembler = assembler

        # A set of used values
        self._used_values = set(self._exclude)

        # The maximum number of attempts to generate unique data that should be
        # performed.
        self._max_attempts = max_attempts

    def reset(self):
        """Reset the set of used values"""
        self._used_values = set(self._exclude)

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
        return self._get_unique()

    def _finish(self, value):
        if self._assembler:
            return self._maker(value)
        return self._get_unique(value)
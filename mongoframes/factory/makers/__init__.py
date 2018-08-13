import contextlib
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

    def __init__(self):

        # The document the maker is assembling/finishing data for
        self._document = None

    def __call__(self, *args):
        if args:
            return self._finish(*args)
        return self._assemble()

    @property
    def document(self):
        # Return the target document
        return self._document

    def reset(self):
        """Reset the maker instance"""
        pass

    def _assemble(self):
        return None

    def _finish(self, value):
        return value

    @contextlib.contextmanager
    def target(self, document):
        self._document = document
        yield
        self._document = None


class DictOf(Maker):
    """
    Make a dictionary of key/values where each value is a set value or generated
    using a maker.
    """

    def __init__(self, table):
        super().__init__()

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
        super().__init__()

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
        super().__init__()

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
            return self._func(self.document)
        return None

    def _finish(self, value):
        if self._finisher:
            return self._func(self.document, value)
        return value


class ListOf(Maker):
    """
    Generate a list of values of the given quantity using the specified maker.
    """

    def __init__(self, maker, quantity, reset_maker=False):
        super().__init__()

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

        with self._maker.target(self.document):
            return [self._maker(v) for v in value]


class Static(Maker):
    """
    A maker that returns a fixed value.
    """

    def __init__(self, value, assembler=True):
        super().__init__()

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
    A maker that generates sub-documents.
    """

    def __init__(self, blueprint):
        super().__init__()

        # The blueprint to produce
        self._blueprint = blueprint

    def reset(self):
        """Reset the blueprint for the maker"""
        self._blueprint.reset()

    def _assemble(self):
        return self._blueprint.assemble()

    def _finish(self, value):
        document = self._blueprint.finish(value)

        # Separate out any meta fields
        meta_document = {}
        for field_name in self._blueprint._meta_fields:
            meta_document[field_name] = document[field_name]
            document.pop(field_name)

        # Initialize the sub-frame
        sub_frame = self._blueprint.get_frame_cls()(document)

        # Apply any meta fields
        for key, value in meta_document.items():
            setattr(sub_frame, key, value)

        return sub_frame


class Unique(Maker):
    """
    Ensure that unique values are generated by a maker.
    """

    def __init__(self,
        maker,
        exclude=None,
        assembler=True,
        max_attempts=1000
        ):
        super().__init__()

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
            with self._maker.target(self.document):
                value = self._maker(value)
        return self._get_unique(value)
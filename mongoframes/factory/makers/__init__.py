import datetime
import jsonpickle
import random
import re

import faker

__all__ = [
    'Faker',
    'Lambda',

    # @@ REMOVE
    'DateBetween'
    ]


class Maker:
    """
    A base class for all Maker classes.
    """

    def __call__(self, *args):
        if args:
            return self._finish(*args)
        return self._assemble()

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

    def __init__(self, provider, lazy=False, **kwargs):

        # The provider that will be used to generate the value
        self._provider = provider

        # Flag indicating if the providers should be called in _assemble (False)
        # or _finish (True).
        self._lazy = lazy

        # The keyword arguments for the provider
        self._kwargs = kwargs

    def _assemble(self):
        if self._lazy:
            return None
        return getattr(self.get_fake(), self._provider)(**self._kwargs)

    def _finish(self, value):
        if not self._lazy:
            return value
        return getattr(self.get_fake(), self._provider)(**self._kwargs)


class Lambda(Maker):
    """
    Use a lambda function to generate a value.
    """

    def __init__(self, func, lazy=False):

        # The function to call
        self._func = func

        # Flag indicating if the lambda should be called in _assemble (False)
        # or _finish (True).
        self._lazy = lazy

    def _assemble(self):
        if self._lazy:
            return None
        return self._func()

    def _finish(self, value):
        if not self._lazy:
            return value
        return self._func()


# @@ Need a mechanism to
# - reference other documents,
# - keep things unique
# - generate sub-documents



# @@ Move or remove date_between

class DateBetween(Maker):
    """
    Return a date between two points.
    """

    def __init__(self, min_date, max_date):
        self._min_date = min_date
        self._max_date = max_date

    def parse_date_obj(self, d):
        # Parse the date string
        result = re.match(
            '(today|tomorrow|yesterday)((\-|\+)(\d+)){0,1}',
            d
            )
        assert result, 'Not a valid date string'

        # Determine the base date
        if result.groups()[0] == 'today':
            d = datetime.date.today()

        elif result.groups()[0] == 'tomorrow':
            d = datetime.date.today() - datetime.timedelta(days=1)

        elif result.groups()[0] == 'yesterday':
            d = datetime.date.today() + datetime.timedelta(days=1)

        # Add any offset
        if result.groups()[1]:
            op = result.groups()[2]
            days = int(result.groups()[3])
            if op == '+':
                d += datetime.timedelta(days=days)
            else:
                d -= datetime.timedelta(days=days)

        return d

    def _assemble(self):
        return None

    def _finish(self, value):
        min_date = self.parse_date_obj(self._min_date)
        max_date = self.parse_date_obj(self._max_date)
        seconds = random.randint(0, int((max_date - min_date).total_seconds()))
        return min_date + datetime.timedelta(seconds=seconds)
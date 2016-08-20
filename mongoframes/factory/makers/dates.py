import datetime
import math
import random
import re

from mongoframes.factory.makers import Maker

__all__ = [
    'DateBetween'
    ]


class DateBetween(Maker):
    """
    Return a date between two dates. Dates can be specified either as
    `datetime.date` instances or as strings of the form:

        "{yesterday|today|tomorrow}{+|-}{no_of_days}"
    """

    def __init__(self, min_date, max_date):
        super().__init__()

        # The date range between which a date will be selected
        self._min_date = min_date
        self._max_date = max_date

    def _assemble(self):
        min_date = self.parse_date(self._min_date)
        max_date = self.parse_date(self._max_date)
        seconds = random.randint(0, int((max_date - min_date).total_seconds()))
        return math.floor(seconds / 86400)

    def _finish(self, value):
        min_date = self.parse_date(self._min_date)
        return min_date + datetime.timedelta(seconds=value * 86400)

    @staticmethod
    def parse_date(d):
        if isinstance(d, datetime.date):
            return d

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
            d = datetime.date.today() + datetime.timedelta(days=1)

        elif result.groups()[0] == 'yesterday':
            d = datetime.date.today() - datetime.timedelta(days=1)

        # Add any offset
        if result.groups()[1]:
            op = result.groups()[2]
            days = int(result.groups()[3])
            if op == '+':
                d += datetime.timedelta(days=days)
            else:
                d -= datetime.timedelta(days=days)

        return d
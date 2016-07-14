import datetime
import json
import random
import re

__all__ = ['Maker']


class Maker:
    """
    A base class for all Maker classes.
    """

    def __call__(self, *args):
        if args:
            return self._dynamic(*args)
        return self._static()

    def _static(self):
        raise NotImplemented()

    def _dynamic(self):
        pass


class Sequence(Maker):
    """
    Generate a sequence of values postfixed by a number.
    """

    def __init__(self, prefix, start_from=1):
        self._prefix = prefix
        self._offset = start_from

    def _static(self):
        value = "{0._prefix}{0._offset}".format(self)
        self._offset += 1
        return value


class DateBetween(Maker):
    """
    Return a date between two points.
    """

    def __init__(self, min_date, max_date):
        self._min_date = min_date
        self._max_date = max_date

    def parse_date_obj(d):
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
            op = result.groups()[1][0]
            days = int(result.groups()[1][1])

            if op == '+':
                d += datetime.timedelta(days=days)
            else:
                d -= datetime.timedelta(days=days)

        return d

    def _static(self):
        return json.dumps([str(self._min_date), str(self._max_date)])

    def _dynamic(self, args):
        [min_date, max_date] = json.loads(args)
        min_date = parse_date_obj(min_date)
        max_date = parse_date_obj(max_date)
        seconds = random.randint(0, int((max_date - min_date).total_seconds()))
        return min_date + datetime.timedelta(seconds=seconds)
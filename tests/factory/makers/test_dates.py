import datetime

from mongoframes.factory.makers import dates as date_makers

from tests.fixtures import *


def test_date_between():
    """
    `DateBetween` makers should return a random date between two given dates.
    """

    # Configured between two `datetime.date` instances
    min_date = datetime.date(2016, 1, 1)
    max_date = datetime.date(2016, 6, 1)
    maker = date_makers.DateBetween(min_date, max_date)

    # Calculate the number of days between the two dates
    days = (max_date - min_date).total_seconds() / 86400

    # Check the assembled result
    assembled = maker._assemble()
    assert assembled >= 0 and assembled <= days

    # Check the finished result
    finished = maker._finish(assembled)
    assert finished == min_date + datetime.timedelta(seconds=assembled * 86400)

    # Configured between two string dates
    maker = date_makers.DateBetween('today-5', 'today+5')

    # Check the assembled result
    assembled = maker._assemble()
    assert assembled >= 0 and assembled <= 10

    # Check the finished result
    min_date = datetime.date.today() - datetime.timedelta(seconds=5 * 86400)
    finished = maker._finish(assembled)
    assert finished == min_date + datetime.timedelta(seconds=assembled * 86400)

    # Check we can correctly parse tomorrow, today, yesterday
    maker_cls = date_makers.DateBetween

    # Today
    assert maker_cls.parse_date('today') == datetime.date.today()

    # Tomorrow
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    assert maker_cls.parse_date('tomorrow') == tomorrow

    # Yesterday
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    assert maker_cls.parse_date('yesterday') == yesterday
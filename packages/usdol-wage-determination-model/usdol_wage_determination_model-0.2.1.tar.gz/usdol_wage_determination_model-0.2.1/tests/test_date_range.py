from datetime import date

from pydantic import ValidationError
from pytest import raises

from .common import check_error
from .data import test_date_range

from usdol_wage_determination_model import DateRange


def test_basic():
    date_range = DateRange(**test_date_range)
    assert date_range.start_date == date.fromisoformat(test_date_range['start_date'])
    assert date_range.end_date == date.fromisoformat(test_date_range['end_date'])


def test_same_day():
    date_range = DateRange(start_date='2025-01-01', end_date='2025-01-01')
    assert date_range.start_date == date(year=2025, month=1, day=1)
    assert date_range.end_date == date(year=2025, month=1, day=1)


def test_default_end():
    date_range = DateRange(start_date='2025-01-01')
    assert date_range.start_date == date(year=2025, month=1, day=1)
    assert date_range.end_date == date.max


def test_end_before_start():
    with raises(ValidationError) as error:
        DateRange(start_date='2025-01-31', end_date='2025-01-01')
    check_error(error, 'Value error, End date of 2025-01-01 cannot be before start date of 2025-01-31')


def test_invalid_start():
    with raises(ValidationError) as error:
        DateRange(start_date='bad', end_date='2025-01-01')
    check_error(error, 'Input should be a valid date or datetime, input is too short')


def test_invalid_end():
    with raises(ValidationError) as error:
        DateRange(start_date='2025-01-01', end_date='bad')
    check_error(error, 'Input should be a valid date or datetime, input is too short')

from copy import deepcopy
from decimal import Decimal

from pydantic import ValidationError
from pytest import raises

from .common import check_error
from .data import test_wage

from usdol_wage_determination_model import Wage


def test_basic():
    wage = Wage(**test_wage)
    assert wage.currency == test_wage['currency']
    assert wage.rate == Decimal(test_wage['rate'])
    assert wage.fringe == Decimal(test_wage['fringe'])


def test_default_currency():
    test_default_currency = deepcopy(test_wage)
    del test_default_currency['currency']
    wage = Wage(rate='123.45', fringe='12.34')
    assert wage.currency == test_wage['currency']
    assert wage.rate == Decimal(test_wage['rate'])
    assert wage.fringe == Decimal(test_wage['fringe'])


def test_alternate_currency():
    test_alt_currency = deepcopy(test_wage)
    test_alt_currency['currency'] = 'EUR'
    wage = Wage(**test_alt_currency)
    assert wage.currency == 'EUR'
    assert wage.rate == Decimal(test_wage['rate'])
    assert wage.fringe == Decimal(test_wage['fringe'])


def test_no_values():
    with raises(ValidationError) as error:
        Wage()
    check_error(error, 'Field required', 2)


def test_bad_currency():
    test_bad_currency = deepcopy(test_wage)
    test_bad_currency['currency'] = 'FOO'
    with raises(ValidationError) as error:
        Wage(**test_bad_currency)
    check_error(error, 'Invalid currency code.')


def test_bad_rate():
    test_bad_currency = deepcopy(test_wage)
    test_bad_currency['rate'] = None
    with raises(ValidationError) as error:
        Wage(**test_bad_currency)
    check_error(error, 'Decimal input should be an integer, float, string or Decimal object')
    test_bad_currency['rate'] = 'foo'
    with raises(ValidationError) as error:
        Wage(**test_bad_currency)
    check_error(error, 'Input should be a valid decimal')
    test_bad_currency['rate'] = '-123.45'
    with raises(ValidationError) as error:
        Wage(**test_bad_currency)
    check_error(error, 'Input should be greater than or equal to 0.0')
    test_bad_currency['rate'] = '12.456'
    with raises(ValidationError) as error:
        Wage(**test_bad_currency)
    check_error(error, 'Decimal input should have no more than 2 decimal places')


def test_bad_fringe():
    test_bad_currency = deepcopy(test_wage)
    test_bad_currency['fringe'] = None
    with raises(ValidationError) as error:
        Wage(**test_bad_currency)
    check_error(error, 'Decimal input should be an integer, float, string or Decimal object')
    test_bad_currency['fringe'] = 'foo'
    with raises(ValidationError) as error:
        Wage(**test_bad_currency)
    check_error(error, 'Input should be a valid decimal')
    test_bad_currency['fringe'] = '-12.34'
    with raises(ValidationError) as error:
        Wage(**test_bad_currency)
    check_error(error, 'Input should be greater than or equal to 0.0')
    test_bad_currency['fringe'] = '12.456'
    with raises(ValidationError) as error:
        Wage(**test_bad_currency)
    check_error(error, 'Decimal input should have no more than 2 decimal places')

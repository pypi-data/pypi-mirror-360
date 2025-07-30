from copy import deepcopy
from datetime import date
from decimal import Decimal

from pydantic import ValidationError
from pytest import raises

from .common import check_error
from .data import test_date_range, test_zone, test_location, test_job, test_wage, test_wage_determination
from .data import bad_decision_numbers, bad_modification_numbers

from usdol_wage_determination_model import ConstructionType, WageDetermination


def test_basic():
    wage_determination = WageDetermination(**test_wage_determination)
    assert wage_determination.decision_number == test_wage_determination['decision_number']
    assert wage_determination.modification_number == test_wage_determination['modification_number']
    assert wage_determination.publication_date == date.fromisoformat(test_wage_determination['publication_date'])
    assert wage_determination.effective.start_date == date.fromisoformat(test_date_range['start_date'])
    assert wage_determination.effective.end_date == date.fromisoformat(test_date_range['end_date'])
    assert wage_determination.active
    assert wage_determination.location.state == test_location['state']
    assert wage_determination.location.county == test_location['county']
    assert wage_determination.location.zone.center.latitude == test_zone['center']['latitude']
    assert wage_determination.location.zone.center.longitude == test_zone['center']['longitude']
    assert wage_determination.location.zone.radius_min == test_zone['radius_min']
    assert wage_determination.location.zone.radius_max == test_zone['radius_max']
    assert wage_determination.construction_type == ConstructionType.building
    assert wage_determination.rate_identifier == test_wage_determination['rate_identifier']
    assert wage_determination.survey_date == date.fromisoformat(test_wage_determination['survey_date'])
    assert wage_determination.job.classification == test_job['classification']
    assert wage_determination.wage.currency == test_wage['currency']
    assert wage_determination.wage.rate == Decimal(test_wage['rate'])
    assert wage_determination.wage.fringe == Decimal(test_wage['fringe'])


def test_bad_decision_numbers():
    for bad_decision_number in bad_decision_numbers:
        test_bad_wage_determination = deepcopy(test_wage_determination)
        test_bad_wage_determination['decision_number'] = bad_decision_number
        with raises(ValidationError) as error:
            WageDetermination(**test_bad_wage_determination)
        if isinstance(bad_decision_number, str):
            check_error(error, 'String should match pattern \'^[A-Z]{2}[0-9]{8}$\'')
        else:
            check_error(error, 'Input should be a valid string')


def test_bad_modification_numbers():
    for bad_modification_number in bad_modification_numbers:
        test_bad_wage_determination = deepcopy(test_wage_determination)
        test_bad_wage_determination['modification_number'] = bad_modification_number
        with raises(ValidationError) as error:
            WageDetermination(**test_bad_wage_determination)
        if isinstance(bad_modification_number, int):
            check_error(error, 'Input should be greater than or equal to 0')
        elif isinstance(bad_modification_number, float):
            check_error(error, 'Input should be a valid integer, got a number with a fractional part')
        else:
            check_error(error, 'Input should be a valid integer')


def test_effective_date_before_publication_date():
    test_bad_wage_determination = deepcopy(test_wage_determination)
    test_bad_wage_determination['publication_date'] = '2026-01-01'
    with raises(ValidationError) as error:
        WageDetermination(**test_bad_wage_determination)
    check_error(error, 'Value error, Effective start date of 2025-01-01 cannot be before ' +
                       'publication date of 2026-01-01')


def test_survey_date_after_publication_date():
    test_bad_wage_determination = deepcopy(test_wage_determination)
    test_bad_wage_determination['survey_date'] = '2026-01-01'
    with raises(ValidationError) as error:
        WageDetermination(**test_bad_wage_determination)
    check_error(error, 'Value error, Survey completion date of 2026-01-01 cannot be after ' +
                       'publication date of 2025-01-01')


def test_serialization():
    wage_determination = WageDetermination(**test_wage_determination)
    serialized_wage_determination = wage_determination.model_dump()
    assert isinstance(serialized_wage_determination, dict)
    deserialized_wage_determination = WageDetermination(**serialized_wage_determination)
    assert wage_determination == deserialized_wage_determination

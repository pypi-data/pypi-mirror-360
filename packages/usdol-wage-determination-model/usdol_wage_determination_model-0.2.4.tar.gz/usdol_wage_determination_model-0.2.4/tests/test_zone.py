from copy import deepcopy

from pydantic import ValidationError
from pydantic_extra_types.coordinate import Coordinate
from pytest import raises

from .common import check_error
from .data import test_zone

from usdol_wage_determination_model import Zone


def test_basic():
    zone = Zone(**test_zone)
    assert zone.center.latitude == test_zone['center']['latitude']
    assert zone.center.longitude == test_zone['center']['longitude']
    assert zone.radius_min == test_zone['radius_min']
    assert zone.radius_max == test_zone['radius_max']


def test_default_radii():
    center = Coordinate(latitude=0.0, longitude=0.0)
    zone = Zone(center=center)
    assert zone.center.latitude == 0.0
    assert zone.center.longitude == 0.0
    assert zone.radius_min == 0.0
    assert zone.radius_max == float('inf')


def test_no_center():
    with raises(ValidationError) as error:
        Zone()
    check_error(error, 'Field required')


def test_bad_center_latitude():
    test_bad_zone = deepcopy(test_zone)
    test_bad_zone['center']['latitude'] = None
    with raises(ValidationError) as error:
        Zone(**test_bad_zone)
    check_error(error, 'Input should be a valid number', 6)
    test_bad_zone['center']['latitude'] = 'foo'
    with raises(ValidationError) as error:
        Zone(**test_bad_zone)
    check_error(error, 'Input should be a valid number, unable to parse string as a number', 6)
    test_bad_zone['center']['latitude'] = 90.1
    with raises(ValidationError) as error:
        Zone(**test_bad_zone)
    check_error(error, 'Input should be less than or equal to 90', 6)
    test_bad_zone['center']['latitude'] = -90.1
    with raises(ValidationError) as error:
        Zone(**test_bad_zone)
    check_error(error, 'Input should be greater than or equal to -90', 6)


def test_bad_center_longitude():
    test_bad_zone = deepcopy(test_zone)
    test_bad_zone['center']['longitude'] = None
    with raises(ValidationError) as error:
        Zone(**test_bad_zone)
    check_error(error, 'Input should be a valid number', 6)
    test_bad_zone['center']['longitude'] = 'foo'
    with raises(ValidationError) as error:
        Zone(**test_bad_zone)
    check_error(error, 'Input should be a valid number, unable to parse string as a number', 6)
    test_bad_zone['center']['longitude'] = 180.1
    with raises(ValidationError) as error:
        Zone(**test_bad_zone)
    check_error(error, 'Input should be less than or equal to 180', 6)
    test_bad_zone['center']['longitude'] = -180.1
    with raises(ValidationError) as error:
        Zone(**test_bad_zone)
    check_error(error, 'Input should be greater than or equal to -180', 6)


def test_bad_radii():
    test_bad_zone = deepcopy(test_zone)
    test_bad_zone['radius_min'] = -1.0
    test_bad_zone['radius_max'] = 1.0
    with raises(ValidationError) as error:
        Zone(**test_bad_zone)
    check_error(error, 'Input should be greater than or equal to 0')
    test_bad_zone['radius_min'] = 1.0
    test_bad_zone['radius_max'] = -1.0
    with raises(ValidationError) as error:
        Zone(**test_bad_zone)
    check_error(error, 'Input should be greater than or equal to 0')


def test_equal_radii():
    test_bad_zone = deepcopy(test_zone)
    test_bad_zone['radius_min'] = 1.0
    test_bad_zone['radius_max'] = 1.0
    with raises(ValidationError) as error:
        Zone(**test_bad_zone)
    check_error(error, 'Value error, Max radius of 1.0 must be larger than min radius of 1.0')


def test_max_radius_smaller_than_min():
    test_bad_zone = deepcopy(test_zone)
    test_bad_zone['radius_min'] = 1.0
    test_bad_zone['radius_max'] = 0.0
    with raises(ValidationError) as error:
        Zone(**test_bad_zone)
    check_error(error, 'Value error, Max radius of 0.0 must be larger than min radius of 1.0')

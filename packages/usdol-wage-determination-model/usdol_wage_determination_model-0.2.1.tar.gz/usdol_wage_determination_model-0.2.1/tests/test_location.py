from .data import test_location

from usdol_wage_determination_model import Location


def test_basic():
    location = Location(**test_location)
    assert location.state == 'CA'
    assert location.county == 'San Diego'
    assert location.zone.center.latitude == 32.7157
    assert location.zone.center.longitude == 117.1611
    assert location.zone.radius_min == 0.0
    assert location.zone.radius_max == 10.0

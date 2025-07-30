import pathlib

import pytest

import preheat_open as po
from preheat_open.api.conftest import mock_adapter
from preheat_open.test import (
    API_KEY,
    MEDIUM_TEST_PERIOD,
    MOCK_LOCATION_ID,
    SHORT_TEST_PERIOD,
    TEST_LOCATION_ID,
)

# # Defining fixture scope
# FIXTURE_SCOPE = "session"

# @pytest.fixture(scope=FIXTURE_SCOPE)
# def configuration():
#     return papi.Configuration.from_file("yaml")

# @pytest.fixture(scope=FIXTURE_SCOPE)
# def medium_period():
#     return MEDIUM_TEST_PERIOD


# @pytest.fixture(scope=FIXTURE_SCOPE)
# def short_period():
#     return SHORT_TEST_PERIOD


# @pytest.fixture(scope=FIXTURE_SCOPE)
# def location():
#     return po.Location(TEST_LOCATION_ID)


# @pytest.fixture(scope=FIXTURE_SCOPE)
# def location_with_devices(location):
#     b = deepcopy(location)
#     b.load_devices()
#     return b


# @pytest.fixture(scope=FIXTURE_SCOPE)
# def location_with_data(location, medium_period):
#     location_new = deepcopy(location)
#     location_new.get_measurements(*medium_period)
#     return location_new


# # Legacy fixtures
# @pytest.fixture(scope=FIXTURE_SCOPE)
# def building_id():
#     return TEST_LOCATION_ID


# @pytest.fixture(scope=FIXTURE_SCOPE)
# def unit_id():
#     return 15312


# @pytest.fixture(scope=FIXTURE_SCOPE)
# def control_unit_id():
#     return 15357


# @pytest.fixture(scope=FIXTURE_SCOPE)
# def unit(location, unit_id):
#     return location.query_units(unit_id=unit_id)[0]


# @pytest.fixture(scope=FIXTURE_SCOPE)
# def unit_with_data(unit, medium_period):
#     unit_new = deepcopy(unit)
#     unit_new.get_measurements(*medium_period)
#     return unit_new


# @pytest.fixture(scope=FIXTURE_SCOPE)
# def control_unit(location):
#     return location.query_units("control", "control_unit_custom_1")[0]


# @pytest.fixture(scope=FIXTURE_SCOPE)
# def weather_unit(location):
#     return location.weather


@pytest.fixture(scope="session")
def location(mock_adapter) -> po.Location:
    return mock_adapter.get_location(MOCK_LOCATION_ID)

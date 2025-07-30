"""
Sub-package containing all test routines to be run with Pytest (parameterized with 'conftest.py')
"""
import os
import warnings
from typing import Union

import pytest

import preheat_open
from preheat_open.time import TimeResolution

# Setting up a test API key, which is only valid for a dummy test installation
MOCK_LOCATION_ID = 1
TEST_LOCATION_ID = 2756
API_KEY = "KVkIdWLKac5XFLCs2loKb7GUitkTL4uJXoSyUFIZkVgWuCk8Uj"
ANONYMISED_API_KEY = "3xa0SeGXa4WlkrB68qGR9NoDAzVvGdiG3XAabKu6n7n5qQTDkL"

SHORT_TEST_PERIOD = (
    "2021-05-01T00:00+02:00",
    "2021-05-02T00:00+02:00",
    TimeResolution.HOUR,
)
MEDIUM_TEST_PERIOD = (
    "2021-05-01T00:00+02:00",
    "2021-05-02T00:00+02:00",
    TimeResolution.HOUR,
)


class PreheatTest:
    @pytest.fixture()
    def bypass_api_key(self):
        preheat_open.ApiSession().set_api_key(None)
        yield None
        preheat_open.ApiSession().set_api_key(API_KEY)


def __clearing_forbidden(*args, **kwargs):
    raise RuntimeError("Clearing of data in fixture for data is forbidden")


def forbid_clear_data_on_object(
    x: Union[preheat_open.Location, preheat_open.unit.Unit]
):
    if isinstance(x, preheat_open.unit.Unit):
        x.clear_data = __clearing_forbidden
    elif isinstance(x, preheat_open.Location):
        x.clear_data = __clearing_forbidden
        [forbid_clear_data_on_object(u) for u in x.list_all_units()]
    else:
        raise TypeError("Input must be a Building or a Unit")

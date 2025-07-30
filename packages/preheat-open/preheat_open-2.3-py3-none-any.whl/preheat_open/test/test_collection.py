from datetime import datetime

import pandas as pd
import pytest

import preheat_open as po
from preheat_open.interfaces import Adapter


@pytest.fixture(scope="session")
def collection(mock_adapter: Adapter):
    loc_info = mock_adapter.get_all_locations_information()
    return po.Collection.from_location_information_list(
        location_information_list=loc_info, adapter=mock_adapter
    )


def test_collection_locations(collection: po.Collection):
    collection.load_building_models()
    assert isinstance(collection.locations, dict)
    assert len(collection.locations) > 0
    for info, loc in collection.locations.items():
        assert isinstance(info, po.LocationInformation)
        assert isinstance(loc, po.Location)


def test_collection_get_measurements(collection: po.Collection):
    df = collection.get_measurements(
        date_range=po.DateRange(
            start=datetime(2024, 6, 1),
            end=datetime(2024, 6, 2),
            resolution=po.TimeResolution.HOUR,
        )
    )
    assert isinstance(df, pd.DataFrame)


def test_collection_get_units(collection: po.Collection):
    units = list(collection.get_units())
    assert all(isinstance(unit, po.Unit) for unit in units)


def test_collection_get_devices(collection: po.Collection):
    devices = list(collection.get_devices())
    assert all(isinstance(device, po.Device) for device in devices)


def test_collection_get_zones(collection: po.Collection):
    zones = list(collection.get_zones())
    assert all(isinstance(zone, po.Zone) for zone in zones)


def test_collection_get_components(collection: po.Collection):
    components = list(collection.get_components())
    assert all(isinstance(component, po.Component) for component in components)


def test_collection_timezone(collection: po.Collection):
    timezone = collection.timezone
    assert timezone.key == "Europe/Copenhagen"  # Assuming default timezone

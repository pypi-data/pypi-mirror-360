import copy
import glob
import pathlib
import random
import string
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import partial
from typing import ClassVar

import numpy as np
import pandas as pd
import yaml
from requests.models import Response

import preheat_open as po
import preheat_open.api as papi


@dataclass
class MockApiAdapter(po.Adapter):
    building_model: ClassVar[po.BuildingModel] = papi.building_model
    mocks_path: str = str(pathlib.Path(__file__).parent.resolve())

    def open(self):
        pass

    def close(self):
        pass

    def get_location(self, location_id: int) -> po.Location:
        path = f"{self.mocks_path}/locations/{location_id}.yaml"
        with open(path, "r") as file:
            building_model_dict = yaml.safe_load(file)
        return po.Location.from_building_model_dict(
            data=building_model_dict, adapter=self
        )

    def get_locations(self, location_ids: list[int]) -> list[po.Location]:
        return [self.get_location(location_id) for location_id in location_ids]

    def get_all_locations_information(self) -> list[po.LocationInformation]:
        directory_path = (
            pathlib.Path(__file__).parent.resolve() / "test/mocks/locations"
        )
        yaml_files = glob.glob(str(directory_path / "*.yaml"))
        loc_info = []
        for file in yaml_files:
            with open(file, "r") as f:
                building_model_dict = yaml.safe_load(f)
            loc = po.Location.from_building_model_dict(
                data=building_model_dict, adapter=self
            )
            loc_info.append(loc.information)
        return loc_info

    def get_all_locations_collection(self) -> po.Collection:
        return po.Collection.from_location_information_list(
            location_information_list=self.get_all_locations_information(),
            adapter=self,
        )

    def get_devices(self, location_id: int) -> list[po.Device]:
        return []

    def load_measurements(
        self,
        components: list[po.Component],
        date_range: po.DateRange,
        timestamp_type: papi.TimestampType = papi.TimestampType.ISO,
    ) -> None:
        for component in components:
            loadabletype = component.measurements[date_range.resolution]
            mocked_data = mock_component_data(
                date_range=date_range, component_type=component.type
            ).rename(
                component.id if isinstance(component.parent, po.Unit) else component.cid
            )
            loadabletype.update(date_range=date_range, data=mocked_data)

    def get_price_components(
        self,
        supply_point_ids: list[int],
    ) -> dict[int, list[po.AppliedPriceComponent]]:
        pass

    def get_price_data(
        self,
        date_range: po.DateRange,
        price_component_ids: list[int],
        timestamp_type: papi.TimestampType = papi.TimestampType.ISO,
    ) -> dict[int, po.PriceData]:
        pass

    def get_setpoint_schedule(
        self,
        date_range: po.DateRange,
        control_unit: po.Unit,
    ) -> po.SetpointSchedule:
        date_range = copy.deepcopy(date_range)
        date_range.resolution = po.TimeResolution.HOUR
        dr = date_range.to_pandas_date_range()
        values = np.random.uniform(10, 50, len(dr))
        return po.SetpointSchedule(
            schedule=[
                po.ScheduleItem(start=t, value=v, operation=po.OperationType.NORMAL)
                for t, v in zip(dr, values)
            ]
        )

    def put_setpoint_schedule(
        self,
        schedule: po.SetpointSchedule,
        control_unit: po.Unit,
    ) -> Response:
        pass

    def get_comfort_profile_setpoints(self, date_range, location) -> po.ComfortProfiles:
        date_range = copy.deepcopy(date_range)
        comfort_profile_ids = (
            cp
            if (cp := [zone.comfort_profile_id for zone in location.get_zones()])
            else [1]
        )
        date_range.resolution = po.TimeResolution.HOUR
        dr = date_range.to_pandas_date_range()
        return po.ComfortProfiles(
            profiles={
                _id: po.ComfortProfile(
                    id=_id, setpoints=[po.Setpoint(time=t, setpoint=21) for t in dr]
                )
                for _id in comfort_profile_ids
            }
        )

    def get_electricity_prices(
        self, date_range, unit, include_vat, include_tariff
    ) -> po.ElectricityPrices:
        date_range = copy.deepcopy(date_range)
        date_range.resolution = po.TimeResolution.HOUR
        dr = date_range.to_pandas_date_range()
        return po.ElectricityPrices(
            data=[
                po.ElectricityPriceItem(time=t, value=np.random.uniform(0, 4))
                for t in dr
            ],
            tariff_included=include_tariff,
            vat_included=include_vat,
        )

    def get_features(self, location_id):
        pass

    def location_post_setup(self, location: po.Location):
        location.comfort_profiles = (
            po.LoadableData(
                data=po.ComfortProfiles(),
                getter=partial(
                    self.get_comfort_profile_setpoints,
                    location=location,
                ),
            )
            if location.comfort_profiles is None
            else location.comfort_profiles
        )
        for u in location.get_units(papi.UnitQuery(type=papi.UnitType.CONTROL)):
            u.setpoint_schedule = (
                po.LoadableData(
                    data=po.SetpointSchedule(),
                    getter=partial(
                        self.get_setpoint_schedule,
                        control_unit=u,
                    ),
                    setter=partial(
                        self.put_setpoint_schedule,
                        control_unit=u,
                    ),
                )
                if u.setpoint_schedule is None
                else u.setpoint_schedule
            )
        for u in location.get_units(
            papi.UnitQuery(type=[papi.UnitType.ELECTRICITY, papi.UnitType.SUB_METER])
        ):
            if (
                u.type == papi.UnitType.SUB_METER
                and u.parent.type != papi.UnitType.ELECTRICITY
            ):
                continue
            elif u.electricity_prices is None:
                u.electricity_prices = {
                    "tariff_included"
                    if t
                    else "tariff_excluded": {
                        "vat_included"
                        if v
                        else "vat_excluded": po.LoadableData(
                            data=po.ElectricityPrices(),
                            getter=partial(
                                self.get_electricity_prices,
                                unit=u,
                                include_vat=v,
                                include_tariff=t,
                            ),
                        )
                        for v in [True, False]
                    }
                    for t in [True, False]
                }


@dataclass
class ComponentCharacteristic(ABC):
    @abstractmethod
    def mock(self, data: pd.Series) -> pd.Series:
        pass


@dataclass
class CCNoisy(ComponentCharacteristic):
    mean: float = 0.0
    std: float = 1.0

    def mock(self, data: pd.Series) -> pd.Series:
        return pd.Series(
            np.random.normal(self.mean, self.std, len(data)), index=data.index
        )


@dataclass
class CCMonotonicAscending(ComponentCharacteristic):
    def mock(self, data: pd.Series) -> pd.Series:
        return data.abs().cumsum()


@dataclass
class CCRangeConstricted(ComponentCharacteristic):
    min: float = 0.0
    max: float = 100.0

    def mock(self, data: pd.Series) -> pd.Series:
        imin = data.min()
        imax = data.max()
        if imin == imax:
            data = pd.Series(
                np.full(len(data), self.max / 2 - self.min / 2), index=data.index
            )
        else:
            data = self.min + (self.max - self.min) * (data - imin) / (imax - imin)
        return data


@dataclass
class CCYearlyPeriodic(ComponentCharacteristic):
    amplitude: float = 1.0
    day_of_year_top: float = 365 / 2

    def mock(self, data: pd.Series) -> pd.Series:
        return data + pd.Series(
            self.amplitude
            * np.sin(2 * np.pi * (data.index.dayofyear - self.day_of_year_top) / 365),
            index=data.index,
        )


@dataclass
class CCDailyPeriodic(ComponentCharacteristic):
    amplitude: float = 1.0
    hour_of_day_top: float = 12

    def mock(self, data: pd.Series) -> pd.Series:
        return data + pd.Series(
            self.amplitude
            * np.sin(2 * np.pi * (data.index.hour - self.hour_of_day_top) / 24),
            index=data.index,
        )


def get_component_type_mocks(
    component_type: papi.ComponentType,
) -> list[ComponentCharacteristic]:
    lookup = {
        papi.ComponentType.FLOW: [CCNoisy(), CCRangeConstricted(min=0.0, max=500.0)],
        papi.ComponentType.SUPPLY_TEMPERATURE: [
            CCNoisy(),
            CCDailyPeriodic(hour_of_day_top=19),
            CCRangeConstricted(min=10, max=100),
        ],
        papi.ComponentType.RETURN_TEMPERATURE: [
            CCNoisy(),
            CCDailyPeriodic(hour_of_day_top=19),
            CCRangeConstricted(min=10, max=100),
        ],
        papi.ComponentType.PRIMARY_SUPPLY_TEMPERATURE: [
            CCNoisy(),
            CCDailyPeriodic(hour_of_day_top=19),
            CCRangeConstricted(min=10, max=100),
        ],
        papi.ComponentType.PRIMARY_RETURN_TEMPERATURE: [
            CCNoisy(),
            CCDailyPeriodic(hour_of_day_top=19),
            CCRangeConstricted(min=10, max=100),
        ],
        papi.ComponentType.VOLUME: [
            CCNoisy(),
            CCYearlyPeriodic(day_of_year_top=30),
            CCRangeConstricted(min=0, max=20),
            CCMonotonicAscending(),
        ],
        papi.ComponentType.ENERGY: [
            CCNoisy(),
            CCYearlyPeriodic(day_of_year_top=30),
            CCRangeConstricted(min=0, max=20),
            CCMonotonicAscending(),
        ],
        papi.ComponentType.POWER: [
            CCNoisy(),
            CCYearlyPeriodic(day_of_year_top=30),
            CCRangeConstricted(min=0, max=20),
        ],
        papi.ComponentType.HP_ON: [CCNoisy(), CCRangeConstricted(min=0.0, max=1.0)],
        papi.ComponentType.MOTOR_POSITION: [
            CCNoisy(),
            CCRangeConstricted(min=0.0, max=100.0),
        ],
        papi.ComponentType.AMBIENT_TEMPERATURE: [
            CCNoisy(),
            CCDailyPeriodic(),
            CCYearlyPeriodic(day_of_year_top=200),
            CCRangeConstricted(min=-10.0, max=40.0),
        ],
        papi.ComponentType.TEMPERATURE: [
            CCNoisy(),
            CCDailyPeriodic(),
            CCYearlyPeriodic(day_of_year_top=200),
            CCRangeConstricted(min=10, max=40),
        ],
        papi.ComponentType.HUMIDITY: [CCNoisy(), CCRangeConstricted(min=50, max=80)],
        papi.ComponentType.CONTROL_INPUT: [
            CCNoisy(),
            CCRangeConstricted(min=50, max=60),
        ],
        papi.ComponentType.CONTROLLED_SIGNAL: [
            CCNoisy(),
            CCRangeConstricted(min=45, max=65),
        ],
    }
    return lookup[component_type] if component_type in lookup else [CCNoisy()]


def mock_component_data(
    date_range: po.DateRange, component_type: papi.ComponentType
) -> pd.Series:
    index = date_range.to_pandas_date_range()
    series = pd.Series(np.zeros(shape=len(index)), index=index)
    for chts in get_component_type_mocks(component_type):
        series = chts.mock(series)
    return series


def generate_random_string(length=8):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


# Helper function to generate unique random integers
def generate_unique_random_ints(count, start=1000, end=9999):
    return random.sample(range(start, end + 1), count)


# Main function to edit the dictionary
def anonymize_building_model_dict(
    building_model_dict: dict, mock_id: int, unit_ids_to_mock: list[int]
) -> tuple[dict, dict[int, int]]:
    random.seed(mock_id)
    mock_unit_mapping = {}
    keys_to_replace = {
        "name": generate_random_string,
        "description": generate_random_string,
        "address": generate_random_string,
        "city": generate_random_string,
        "country": generate_random_string,
        "label": generate_random_string,
        "postcode": generate_random_string,
        "organisation_name": generate_random_string,
        "parent_organisation_name": generate_random_string,
        "latitude": lambda: random.uniform(0, 90),
        "longitude": lambda: random.uniform(0, 180),
        "area": lambda: random.uniform(0, 1000),
        "zipcode": lambda: str(random.randint(1000, 9999)),
    }
    dictionary = {}

    def anonymize(key, d, ids, pkey="information"):
        if isinstance(d, dict):
            return {k: anonymize(k, v, ids, key) for k, v in d.items()}
        elif isinstance(d, list):
            return [anonymize(key, v, ids, pkey) for v in d]
        elif key in keys_to_replace:
            return keys_to_replace[key]()
        elif d is None:
            return None
        elif key.endswith("id") or key.endswith("Id"):
            if key == "unit_id":
                key = "id"
                pkey = "children"
            dkey = f"{pkey}_{key}_{d}"
            if dkey in dictionary:
                return dictionary[dkey]
            dictionary[dkey] = ids.pop()
            if d in unit_ids_to_mock:
                mock_unit_mapping[d] = dictionary[dkey]
            return dictionary[dkey]
        else:
            return d

    # Generate unique random integers for keys ending in "id"
    unique_ints = generate_unique_random_ints(10000, end=99999)

    anon = anonymize("information", building_model_dict, unique_ints)

    def add_consistency(key, d):
        if isinstance(d, dict):
            return {k: add_consistency(k, v) for k, v in d.items()}
        elif isinstance(d, list):
            return [add_consistency(key, v) for v in d]
        elif key == "related_units":
            for key_try in [f"children_id_{d}", f"units_id_{d}"]:
                if key_try in dictionary:
                    return dictionary[key_try]
        elif key in ("zones", "adjacentZones"):
            for key_try in [f"zones_id_{d}", f"subZones_id_{d}"]:
                if key_try in dictionary:
                    return dictionary[key_try]
        else:
            return d

    anon = add_consistency(None, anon)

    anon["id"] = mock_id
    anon["information"]["id"] = mock_id

    return anon, mock_unit_mapping

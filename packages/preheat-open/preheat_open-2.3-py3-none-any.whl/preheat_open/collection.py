import logging
from dataclasses import dataclass, field
from typing import Callable, Generator

import pandas as pd

from preheat_open.api.configuration import PersonalConfig

from .interfaces import Adapter
from .location import Location, LocationInformation
from .measurements import get_measurements
from .query import Query
from .time import ZoneInfo, tzinfo
from .unit import Component, Device, Unit
from .zone import Zone

logger = logging.getLogger(__name__)


@dataclass
class Collection:
    """
    Represents a collection of locations.

    :ivar locations: The locations in the collection.
    """

    locations: dict[LocationInformation, Location] = field(default_factory=dict)
    adapter: Adapter = None
    _models_loaded: bool = field(default=False)
    """
    The locations in the collection.
    """

    def __post_init__(self) -> None:
        """
        Post-initialization processing to set up the collection.
        """
        if all([loc is not None for loc in self.locations.values()]):
            self._models_loaded = True

    @classmethod
    def from_location_ids(
        cls, location_ids: list[int], adapter: Adapter, **kwargs
    ) -> "Collection":
        """
        Creates a collection from a list of locations.

        :param location_list: The list of locations.
        :return: The collection.
        """
        locations = adapter.get_locations(location_ids)
        return cls(
            locations={l.information: l for l in locations},
            adapter=adapter,
            **kwargs,
        )

    @classmethod
    def from_location_information_list(
        cls, location_information_list: list[LocationInformation], **kwargs
    ) -> "Collection":
        """
        Creates a collection from a list of location information.

        :param location_information_list: The list of location information.
        :return: The collection.
        """
        return cls(
            locations={loc_info: None for loc_info in location_information_list},
            **kwargs,
        )

    def get_keys(self, **kwargs) -> Generator[None, None, LocationInformation]:
        for loc_info in self.locations.keys():
            if all(getattr(loc_info, key) == value for key, value in kwargs.items()):
                yield loc_info

    def load_building_models(self) -> None:
        """
        Loads the building models for each location in the collection.
        """
        ids_to_load = [
            loc_info.id for loc_info, model in self.locations.items() if model is None
        ]
        if ids_to_load:
            models = self.adapter.get_locations(ids_to_load)
            for model in models:
                key = next(self.get_keys(id=model.id))
                self.locations[key] = model

    def filter(self, location_info_filter: Callable) -> "Collection":
        """
        Filters the collection based on a filter function.

        :param filter_func: The filter function.
        :return: The filtered collection.
        """
        return Collection(
            locations={
                loc_info: loc
                for loc_info, loc in self.locations.items()
                if location_info_filter(loc_info)
            },
            adapter=self.adapter,
        )

    def get_measurements(
        self,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Retrieves measurements for the location.

        :param components: The components to get measurements for.
        :type components: list[Component] | Query | dict
        :param date_range: The date range for the measurements.
        :type date_range: DateRange, optional
        :param mapper: The mapper to apply to the measurements.
        :type mapper: MapApplier, optional
        :param kwargs: Additional arguments.
        :return: A DataFrame containing the measurements.
        :rtype: pd.DataFrame
        """
        if not self._models_loaded:
            self.load_building_models()
        return get_measurements(
            obj=self,
            **kwargs,
        )

    def get_units(
        self,
        query: Query | None = None,
        **kwargs,
    ) -> Generator[Unit, None, None]:
        """
        Retrieves units associated with the location.

        :param query: The query to filter units.
        :type query: Query, optional
        :param kwargs: Additional arguments.
        :return: A generator yielding units.
        :rtype: Generator[Unit, None, None]
        """
        if not self._models_loaded:
            self.load_building_models()
        for location in self.locations.values():
            yield from location.get_units(
                query=query,
                **kwargs,
            )

    def get_devices(
        self,
        query: Query | list[Query] | None = None,
        **kwargs,
    ) -> Generator[Device, None, None]:
        """
        Retrieves devices associated with the location.

        :param query: The query to filter devices.
        :type query: Query, optional
        :param kwargs: Additional arguments.
        :return: A generator yielding devices.
        :rtype: Generator[Device, None, None]
        """
        if not self._models_loaded:
            self.load_building_models()
        for location in self.locations.values():
            yield from location.get_devices(
                query=query,
                **kwargs,
            )

    def get_zones(
        self,
        query: Query | list[Query] | None = None,
        **kwargs,
    ) -> Generator[Zone, None, None]:
        """
        Retrieves zones associated with the location.

        :param query: The query to filter zones.
        :type query: Query, optional
        :param kwargs: Additional arguments.
        :return: A generator yielding zones.
        :rtype: Generator[Zone, None, None]
        """
        if not self._models_loaded:
            self.load_building_models()
        for location in self.locations.values():
            yield from location.get_zones(
                query=query,
                **kwargs,
            )

    def get_components(
        self,
        query: Query | list[Query] | None = None,
        **kwargs,
    ) -> Generator[Component, None, None]:
        """
        Retrieves components associated with the location.

        :param query: The query to filter components.
        :type query: Query | list[Query], optional
        :param kwargs: Additional arguments.
        :return: A generator yielding components.
        :rtype: Generator[Component, None, None]
        """
        if not self._models_loaded:
            self.load_building_models()
        for location in self.locations.values():
            yield from location.get_components(
                query=query,
                **kwargs,
            )

    @property
    def timezone(self) -> tzinfo:
        """
        The timezone of the location.

        :return: The timezone.
        :rtype: str
        """
        if hasattr(self.adapter, "configuration"):
            timezone = ZoneInfo(PersonalConfig().timezone)
            logger.debug(
                f"Tried using timezone on {self.__class__.__name__}. Fallback to timezone from configuration: {timezone}"
            )
        else:
            timezone = ZoneInfo("Europe/Copenhagen")
            logger.debug(
                f"Tried using timezone on {self.__class__.__name__}. Fallback to default timezone: {timezone}"
            )
        return timezone

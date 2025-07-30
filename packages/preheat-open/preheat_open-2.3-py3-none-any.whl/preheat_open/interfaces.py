from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, ClassVar, TypeVar, final

from requests.models import Response

from .loadable_types import ComfortProfile, ElectricityPrices
from .time import DateRange

if TYPE_CHECKING:
    from .collection import Collection
    from .loadable_types import SetpointSchedule
    from .location import Location, LocationInformation
    from .supplypoint import AppliedPriceComponent, PriceData
    from .unit import Component, Device, Unit

logger = logging.getLogger(__name__)


def log_method_call(logger=logger, level="debug"):
    def decorator(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            # Format the arguments and keyword arguments
            args_str = ", ".join(repr(arg) for arg in args)
            kwargs_str = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
            all_args_str = ", ".join(filter(None, [args_str, kwargs_str]))

            # Log the formatted message
            getattr(logger, level)(
                "%s.%s(%s)",
                self.__class__.__name__,
                method.__name__,
                all_args_str,
            )
            return method(self, *args, **kwargs)

        return wrapper

    return decorator


@dataclass
class BuildingModel:
    component_query_type: type
    component_type: type
    unit_query_type: type
    unit_type: type
    unit_subtype: type
    device_query_type: type
    device_type: type
    zone_query_type: type
    zone_type: type
    control_setting_type: type


T = TypeVar("T", bound="Adapter")


@dataclass
class Adapter(ABC):
    building_model: ClassVar[BuildingModel]

    @abstractmethod
    def open(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    def __enter__(self: T) -> T:
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        self.close()
        return False

    @abstractmethod
    def get_features(self, location_id: int):
        pass

    @abstractmethod
    def get_all_locations_information(self) -> list[LocationInformation]:
        pass

    @abstractmethod
    def get_all_locations_collection(self) -> Collection:
        pass

    @abstractmethod
    def get_location(self, location_id: int) -> Location:
        pass

    @abstractmethod
    def get_locations(self, location_ids: list[int]) -> list[Location]:
        pass

    @abstractmethod
    def get_devices(self, location_id: int) -> list[Device]:
        pass

    @abstractmethod
    def load_measurements(
        self,
        components: list[Component],
        date_range: DateRange,
    ) -> None:
        pass

    @abstractmethod
    def get_comfort_profile_setpoints(
        self, date_range: DateRange, location: Location | int
    ) -> list[ComfortProfile]:
        pass

    @abstractmethod
    def get_price_components(
        self,
        supply_point_ids: list[int],
    ) -> dict[int, list[AppliedPriceComponent]]:
        pass

    @abstractmethod
    def get_price_data(
        self,
        date_range: DateRange,
        price_component_ids: list[int],
    ) -> dict[int, PriceData]:
        pass

    @abstractmethod
    def put_setpoint_schedule(
        self, schedule: SetpointSchedule, control_unit: Unit
    ) -> Response:
        pass

    @abstractmethod
    def get_setpoint_schedule(
        self,
        control_unit: Unit,
        date_range: DateRange,
    ) -> SetpointSchedule:
        pass

    @abstractmethod
    def get_electricity_prices(
        self,
        unit: Unit,
        date_range: DateRange,
        include_vat: bool,
        include_tariff: bool,
    ) -> ElectricityPrices:
        pass

    def location_post_setup(self, location: Location) -> None:
        pass

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for method_name in dir(cls):
            if any(method_name.startswith(s) for s in ["get_", "put_", "load_"]):
                method = getattr(cls, method_name, None)
                if method and not hasattr(method, "_is_logged"):
                    # Apply decorator and mark the method as already decorated
                    logged_method = log_method_call(logger=logger)(method)
                    setattr(logged_method, "_is_logged", True)
                    setattr(cls, method_name, logged_method)


class Factory(ABC):
    _return_class: Callable
    _translation_dict: dict[str, str]

    def __init__(self, input_dict: dict[str, Any] = {}) -> None:
        self.input_dict = input_dict

    def make_sub_classes(self) -> None:
        pass

    @final
    def build(self, **kwargs) -> Any:
        self.input_dict.update(kwargs)
        self.make_sub_classes()
        obj = self._return_class(
            **{
                key: self.input_dict.pop(val)
                for key, val in self._translation_dict.items()
                if val in self.input_dict
            }
        )
        for key, val in self.input_dict.items():
            logger.warning(
                "Unused key-value pair in %s: (%s: %s) Context: %s",
                self.__class__,
                key,
                val,
                obj,
            )
        return obj

    @classmethod
    def translate(self, obj) -> Any:
        if isinstance(obj, self._return_class):
            return {
                val: getattr(obj, key) for key, val in self._translation_dict.items()
            }
        else:
            raise TypeError(
                f"Wrong object type to translate, received {type(obj)} but expected {self._return_class}."
            )

"""Asynchronous Python client for Powerfox."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin


class DeviceType(int, Enum):
    """Enum for the different device types."""

    NO_TYPE = -1
    POWER_METER = 0
    COLD_WATER_METER = 1
    HOT_WATER_METER = 2
    HEAT_METER = 3
    GAS_METER = 4
    COLD_HOT_WATER_METER = 5

    @property
    def human_readable(self) -> str:
        """Return a human readable string for the device type."""
        return {
            DeviceType.POWER_METER: "Power Meter",
            DeviceType.COLD_WATER_METER: "Cold Water Meter",
            DeviceType.HOT_WATER_METER: "Hot Water Meter",
            DeviceType.HEAT_METER: "Heat Meter",
            DeviceType.GAS_METER: "Gas Meter",
            DeviceType.COLD_HOT_WATER_METER: "Cold/Hot Water Meter",
        }.get(self, "Unknown")


@dataclass
class Device(DataClassORJSONMixin):
    """Object representing a Device from Powerfox."""

    id: str = field(metadata=field_options(alias="DeviceId"))
    date_added: datetime = field(
        metadata=field_options(
            alias="AccountAssociatedSince",
            deserialize=lambda x: datetime.fromtimestamp(x, tz=UTC),
        )
    )
    main_device: bool = field(metadata=field_options(alias="MainDevice"))
    bidirectional: bool = field(metadata=field_options(alias="Prosumer"))
    type: DeviceType = field(metadata=field_options(alias="Division"))
    name: str = field(metadata=field_options(alias="Name"), default="Poweropti")


@dataclass
class Poweropti(DataClassORJSONMixin):
    """Object representing a Poweropti device."""

    outdated: bool = field(metadata=field_options(alias="Outdated"))
    timestamp: datetime = field(
        metadata=field_options(
            alias="Timestamp",
            deserialize=lambda x: datetime.fromtimestamp(x, tz=UTC),
        )
    )


@dataclass
class PowerMeter(Poweropti):
    """Object representing a Power device."""

    power: int = field(metadata=field_options(alias="Watt"))
    energy_usage: float | None = field(
        metadata=field_options(
            alias="A_Plus",
            deserialize=lambda x: x if x != 0 else None,
        ),
    )
    energy_return: float | None = field(
        metadata=field_options(
            alias="A_Minus",
            deserialize=lambda x: x if x != 0 else None,
        ),
    )
    energy_usage_high_tariff: float | None = field(
        metadata=field_options(alias="A_Plus_HT"), default=None
    )
    energy_usage_low_tariff: float | None = field(
        metadata=field_options(alias="A_Plus_NT"), default=None
    )


@dataclass
class HeatMeter(Poweropti):
    """Object representing a Heat device."""

    total_energy: int = field(metadata=field_options(alias="KiloWattHour"))
    delta_energy: int = field(metadata=field_options(alias="DeltaKiloWattHour"))
    total_volume: float = field(metadata=field_options(alias="CubicMeter"))
    delta_volume: float = field(metadata=field_options(alias="DeltaCubicMeter"))


@dataclass
class WaterMeter(Poweropti):
    """Object representing a Water device."""

    cold_water: float = field(metadata=field_options(alias="CubicMeterCold"))
    warm_water: float = field(metadata=field_options(alias="CubicMeterWarm"))

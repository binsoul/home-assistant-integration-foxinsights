"""Platform for sensor integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import FoxInsightsDataUpdateCoordinator
from .sensors.BatteryLevelSensor import BatteryLevelSensor
from .sensors.CurrentMeteringAtSensor import CurrentMeteringAtSensor
from .sensors.DaysReachSensor import DaysReachSensor
from .sensors.EnergyConsumptionSensor import EnergyConsumptionSensor
from .sensors.FillLevelPercentSensor import FillLevelPercentSensor
from .sensors.FillLevelQuantitySensor import FillLevelQuantitySensor
from .sensors.MaterialConsumptionSensor import MaterialConsumptionSensor
from .sensors.NextMeteringAtSensor import NextMeteringAtSensor
from .sensors.ValidationErrorSensor import ValidationErrorSensor


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensors."""
    coordinator: FoxInsightsDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for device in coordinator.data.values():
        entities.append(FillLevelQuantitySensor(coordinator, device))
        entities.append(FillLevelPercentSensor(coordinator, device))
        entities.append(BatteryLevelSensor(coordinator, device))
        entities.append(CurrentMeteringAtSensor(coordinator, device))
        entities.append(NextMeteringAtSensor(coordinator, device))
        entities.append(MaterialConsumptionSensor(coordinator, device))
        entities.append(EnergyConsumptionSensor(coordinator, device))
        entities.append(DaysReachSensor(coordinator, device))
        entities.append(ValidationErrorSensor(coordinator, device))

    async_add_entities(entities)

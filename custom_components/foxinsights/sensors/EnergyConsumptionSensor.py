"""Sensor for the energy consumption."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfEnergy
from homeassistant.core import callback

from ..api import FoxInsightsDevice
from ..const import LOGGER, NAME
from ..coordinator import FoxInsightsDataUpdateCoordinator
from ..entity import FoxInsightsEntity


class EnergyConsumptionSensor(FoxInsightsEntity):
    """Sensor for the energy consumption."""

    KWH_PER_L_HEATING_OIL_EXTRA_LIGHT = 10.08

    def __init__(
        self, coordinator: FoxInsightsDataUpdateCoordinator, device: FoxInsightsDevice
    ):
        """Initialize."""
        super().__init__(coordinator, device)

        self._attr_unique_id = NAME + "-" + self.device.hwid + "-energyConsumption"
        self._attr_name = NAME + " " + self.device.hwid + " energy consumption"
        self._attr_icon = "mdi:barrel"
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_device_class = SensorDeviceClass.ENERGY

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()

        state = await self.async_get_last_state()

        if state is not None:
            try:
                self._attr_native_value = float(state.state)
                LOGGER.debug(
                    "Restored value for energyConsumption: %s", self._attr_native_value
                )
            except ValueError:
                self._attr_native_value = None
                LOGGER.debug(
                    "Invalid stored value for energyConsumption: %s", state.state
                )

            value = state.attributes.get("previous_value")
            if value is None:
                self._attr_extra_state_attributes["previous_value"] = 0
            else:
                self._attr_extra_state_attributes["previous_value"] = int(value)

            value = state.attributes.get("current_value")
            if value is None:
                self._attr_extra_state_attributes["current_value"] = 0
            else:
                self._attr_extra_state_attributes["current_value"] = int(value)

        data = self.coordinator.get_data(self.device)
        if data is not None and data.fillLevelQuantity is not None:
            self._handle_coordinator_update()

    @callback
    def _handle_coordinator_update(self) -> None:
        if not self.coordinator.needs_update(self.device):
            return None

        data = self.coordinator.get_data(self.device)
        if data is None or data.fillLevelQuantity is None:
            self._attr_native_value = 0.0
            LOGGER.debug("Data for fillLevelQuantity not available")
        else:
            attributes = self._attr_extra_state_attributes
            if "current_value" not in attributes or attributes["current_value"] is None:
                attributes["current_value"] = 0.0

            if (
                "previous_value" not in attributes
                or attributes["previous_value"] is None
            ):
                attributes["previous_value"] = 0.0

            try:
                attributes["previous_value"] = attributes["current_value"]
                attributes["current_value"] = int(data.fillLevelQuantity)

                if self._attr_native_value is None:
                    self._attr_native_value = 0.0

                if attributes["previous_value"] > attributes["current_value"]:
                    diff = attributes["previous_value"] - attributes["current_value"]
                    self._attr_native_value = float(
                        self._attr_native_value
                        + (self.KWH_PER_L_HEATING_OIL_EXTRA_LIGHT * diff)
                    )

                LOGGER.debug(
                    "Update energyConsumption for HWID %s with value: %s",
                    self.device.hwid,
                    self._attr_native_value,
                )
            except ValueError:
                LOGGER.debug(
                    "Invalid value for energyConsumption for HWID %s: %s",
                    self.device.hwid,
                    data.fillLevelQuantity,
                )

            self._attr_extra_state_attributes = attributes

        self.async_write_ha_state()
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return True

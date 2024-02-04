"""Sensor for the fillLevelPercent property."""

from __future__ import annotations

from homeassistant.components.sensor import SensorStateClass
from homeassistant.const import PERCENTAGE, STATE_UNAVAILABLE
from homeassistant.core import callback

from ..api import FoxInsightsDevice
from ..const import LOGGER, NAME
from ..coordinator import FoxInsightsDataUpdateCoordinator
from ..entity import FoxInsightsEntity


class FillLevelPercentSensor(FoxInsightsEntity):
    """Sensor for the fillLevelPercent property."""

    def __init__(
        self, coordinator: FoxInsightsDataUpdateCoordinator, device: FoxInsightsDevice
    ):
        """Initialize."""
        super().__init__(coordinator, device)

        self._attr_unique_id = NAME + "-" + self.device.hwid + "-fillLevelPercent"
        self._attr_name = NAME + " " + self.device.hwid + " fill level percent"
        self._attr_icon = "mdi:percent"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_class = None

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()

        if last_state is not None and last_state.state != STATE_UNAVAILABLE:
            last_sensor_data = await self.async_get_last_sensor_data()

            if last_sensor_data is not None:
                self._attr_native_value = last_sensor_data.native_value
                LOGGER.debug(
                    "Restored value for fillLevelPercent from data: %s",
                    self._attr_native_value,
                )
            else:
                try:
                    self._attr_native_value = int(last_state.state)
                    LOGGER.debug(
                        "Restored value for fillLevelPercent from state: %s",
                        self._attr_native_value,
                    )
                except ValueError:
                    self._attr_native_value = None
                    LOGGER.debug(
                        "Invalid stored value for fillLevelPercent: %s",
                        last_state.state,
                    )

        data = self.coordinator.get_data(self.device)
        if data is not None and data.fillLevelPercent is not None:
            self._handle_coordinator_update()

    @callback
    def _handle_coordinator_update(self) -> None:
        if not self.coordinator.needs_update(self.device):
            return None

        data = self.coordinator.get_data(self.device)
        if data is None or data.fillLevelPercent is None:
            self._attr_native_value = None
            LOGGER.debug("Data for fillLevelPercent not available")
        else:
            try:
                self._attr_native_value = int(data.fillLevelPercent)
                LOGGER.debug(
                    "Update fillLevelPercent for HWID %s with value: %s",
                    self.device.hwid,
                    self._attr_native_value,
                )
            except ValueError:
                LOGGER.debug(
                    "Invalid value for fillLevelPercent for HWID %s: %s",
                    self.device.hwid,
                    data.fillLevelPercent,
                )

        self.async_write_ha_state()
        return None

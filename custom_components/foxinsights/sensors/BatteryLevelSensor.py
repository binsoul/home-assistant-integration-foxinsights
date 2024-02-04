"""Sensor for the batteryLevel property."""
from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import PERCENTAGE, STATE_UNAVAILABLE
from homeassistant.core import callback

from ..api import FoxInsightsDevice
from ..const import LOGGER, NAME
from ..coordinator import FoxInsightsDataUpdateCoordinator
from ..entity import FoxInsightsEntity


class BatteryLevelSensor(FoxInsightsEntity):
    """Sensor for the batteryLevel property."""

    battery_mapping = {
        "FULL": 100,
        "GOOD": 70,
        "MEDIUM": 50,
        "WARNING": 20,
        "CRITICAL": 0,
    }

    def __init__(
        self, coordinator: FoxInsightsDataUpdateCoordinator, device: FoxInsightsDevice
    ):
        """Initialize."""
        super().__init__(coordinator, device)

        self._attr_unique_id = NAME + "-" + self.device.hwid + "-batteryLevel"
        self._attr_name = NAME + " " + self.device.hwid + " battery level"
        self._attr_icon = "mdi:battery"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_state_class = None
        self._attr_device_class = SensorDeviceClass.BATTERY

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()

        if last_state is not None and last_state.state != STATE_UNAVAILABLE:
            last_sensor_data = await self.async_get_last_sensor_data()

            if last_sensor_data is not None:
                self._attr_native_value = last_sensor_data.native_value
                LOGGER.debug(
                    "Restored value for batteryLevel from data: %s",
                    self._attr_native_value,
                )
            else:
                try:
                    self._attr_native_value = str(last_state.state)
                    LOGGER.debug(
                        "Restored value for batteryLevel from state: %s",
                        self._attr_native_value,
                    )
                except ValueError:
                    self._attr_native_value = None
                    LOGGER.debug(
                        "Invalid stored value for batteryLevel: %s", last_state.state
                    )

        data = self.coordinator.get_data(self.device)
        if data is not None and data.batteryLevel is not None:
            self._handle_coordinator_update()

    @callback
    def _handle_coordinator_update(self) -> None:
        if not self.coordinator.needs_update(self.device):
            return None

        data = self.coordinator.get_data(self.device)
        if data is None or data.batteryLevel is None:
            self._attr_native_value = None
            LOGGER.debug("Data for batteryLevel not available")
        else:
            try:
                self._attr_native_value = self.battery_mapping[data.batteryLevel]
                LOGGER.debug(
                    "Update batteryLevel for HWID %s with value: %s",
                    self.device.hwid,
                    self._attr_native_value,
                )
            except KeyError:
                LOGGER.debug(
                    "Invalid value for batteryLevel for HWID %s: %s",
                    self.device.hwid,
                    data.batteryLevel,
                )

        self.async_write_ha_state()
        return None

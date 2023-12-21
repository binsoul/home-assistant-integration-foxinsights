"""Sensor for the daysReach property."""
from __future__ import annotations

from homeassistant.const import TIME_DAYS
from homeassistant.core import callback

from ..api import FoxInsightsDevice
from ..const import LOGGER, NAME
from ..coordinator import FoxInsightsDataUpdateCoordinator
from ..entity import FoxInsightsEntity


class DaysReachSensor(FoxInsightsEntity):
    """Sensor for the daysReach property."""

    def __init__(
        self, coordinator: FoxInsightsDataUpdateCoordinator, device: FoxInsightsDevice
    ):
        """Initialize."""
        super().__init__(coordinator, device)

        self._attr_unique_id = NAME + "-" + self.device.hwid + "-daysReach"
        self._attr_name = NAME + " " + self.device.hwid + " days reach"
        self._attr_icon = "mdi:calendar-range"
        self._attr_native_unit_of_measurement = TIME_DAYS
        self._attr_state_class = None
        self._attr_device_class = None

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()

        state = await self.async_get_last_state()

        if state is not None:
            try:
                self._attr_native_value = int(state.state)
                LOGGER.debug(
                    "Restored value for daysReach: %s", self._attr_native_value
                )
            except ValueError:
                self._attr_native_value = None
                LOGGER.debug("Invalid stored value for daysReach: %s", state.state)

        data = self.coordinator.get_data(self.device)
        if data is not None and data.daysReach is not None:
            self._handle_coordinator_update()

    @callback
    def _handle_coordinator_update(self) -> None:
        if not self.coordinator.needs_update(self.device):
            return None

        data = self.coordinator.get_data(self.device)
        if data is None or data.daysReach is None:
            self._attr_native_value = None
            LOGGER.debug("Data for daysReach not available")
        else:
            try:
                self._attr_native_value = int(data.daysReach)
                LOGGER.debug(
                    "Update daysReach for HWID %s with value: %s",
                    self.device.hwid,
                    self._attr_native_value,
                )
            except ValueError:
                LOGGER.debug(
                    "Invalid value for daysReach for HWID %s: %s",
                    self.device.hwid,
                    data.daysReach,
                )

        self.async_write_ha_state()
        return None

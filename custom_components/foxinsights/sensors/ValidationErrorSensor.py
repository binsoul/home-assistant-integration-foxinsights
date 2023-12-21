"""Sensor for the validationError property."""
from __future__ import annotations

from homeassistant.core import callback

from ..api import FoxInsightsDevice
from ..const import LOGGER, NAME
from ..coordinator import FoxInsightsDataUpdateCoordinator
from ..entity import FoxInsightsEntity


class ValidationErrorSensor(FoxInsightsEntity):
    """Sensor for the validationError property."""

    validation_error_mapping = {
        "NO_ERROR": "No error",
        "NO_METERING": "No measurement yet",
        "EMPTY_METERING": "Incorrect Measurement",
        "NO_EXTRACTED_VALUE": "No fill level detected",
        "SENSOR_CONFIG": "Faulty measurement",
        "MISSING_STORAGE_CONFIG": "Storage configuration missing",
        "INVALID_STORAGE_CONFIG": "Incorrect storage configuration",
        "DISTANCE_TOO_SHORT": "Measured distance too small",
        "ABOVE_STORAGE_MAX": "Storage full",
        "BELOW_STORAGE_MIN": "Calculated filling level implausible",
    }

    def __init__(
        self, coordinator: FoxInsightsDataUpdateCoordinator, device: FoxInsightsDevice
    ):
        """Initialize."""
        super().__init__(coordinator, device)

        self._attr_unique_id = NAME + "-" + self.device.hwid + "-validationError"
        self._attr_name = NAME + " " + self.device.hwid + " validation error"
        self._attr_icon = "mdi:message-alert"
        self._attr_native_unit_of_measurement = None
        self._attr_state_class = None
        self._attr_device_class = None

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()

        state = await self.async_get_last_state()

        if state is not None:
            try:
                if state.state not in self.validation_error_mapping:
                    self._attr_native_value = None
                    LOGGER.debug(
                        "Invalid stored value for validationError: %s", state.state
                    )
                else:
                    self._attr_native_value = str(state.state)
                    LOGGER.debug(
                        "Restored value for validationError: %s",
                        self._attr_native_value,
                    )
            except ValueError:
                self._attr_native_value = None
                LOGGER.debug(
                    "Invalid stored value for validationError: %s", state.state
                )

        data = self.coordinator.get_data(self.device)
        if data is not None:
            self._handle_coordinator_update()

    @callback
    def _handle_coordinator_update(self) -> None:
        if not self.coordinator.needs_update(self.device):
            return None

        data = self.coordinator.get_data(self.device)
        if data is None or data.validationError is None:
            self._attr_native_value = self.validation_error_mapping["NO_ERROR"]
            LOGGER.debug("Data for validationError not available")
        else:
            try:
                self._attr_native_value = self.validation_error_mapping[
                    data.validationError
                ]
                LOGGER.debug(
                    "Update validationError for HWID %s with value: %s",
                    self.device.hwid,
                    self._attr_native_value,
                )
            except KeyError:
                self._attr_native_value = data.validationError
                LOGGER.debug(
                    "Invalid value for validationError for HWID %s: %s",
                    self.device.hwid,
                    data.validationError,
                )

        self.async_write_ha_state()
        return None

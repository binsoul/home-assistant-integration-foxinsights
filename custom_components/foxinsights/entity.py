"""FoxInsightsEntity class."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import FoxInsightsDevice
from .const import DOMAIN, NAME
from .coordinator import FoxInsightsDataUpdateCoordinator


class FoxInsightsEntity(CoordinatorEntity, SensorEntity, RestoreEntity):
    """Class representing a FoxInsights entity."""

    def __init__(
        self, coordinator: FoxInsightsDataUpdateCoordinator, device: FoxInsightsDevice
    ):
        """Initialize the object."""
        super().__init__(coordinator)
        self.device = device

        self._attr_unique_id = coordinator.config_entry.entry_id
        self._attr_native_value = None
        self._attr_extra_state_attributes = {}

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device.hwid)},
            name=NAME + " " + device.hwid,
            serial_number=device.hwid,
            manufacturer=NAME,
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return not self.coordinator.is_unavailable()

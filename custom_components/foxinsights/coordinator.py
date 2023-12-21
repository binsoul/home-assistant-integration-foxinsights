"""DataUpdateCoordinator for FoxInsights."""

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import (
    FoxInsightsApi,
    FoxInsightsApiAuthenticationError,
    FoxInsightsApiConnectionError,
    FoxInsightsApiError,
    FoxInsightsDevice,
)
from .const import DOMAIN, LOGGER


class FoxInsightsDataUpdateCoordinator(
    DataUpdateCoordinator[dict[str, FoxInsightsDevice]]
):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, api: FoxInsightsApi) -> None:
        """Initialize."""
        self.api = api
        self.update_datetime: dict[str, str] = {}
        self.update_flag: dict[str, bool] = {}

        super().__init__(
            hass, LOGGER, name=DOMAIN, update_interval=timedelta(minutes=15)
        )

    async def _async_update_data(self) -> dict[str, FoxInsightsDevice]:
        """Update data via API."""
        try:
            devices = await self.api.async_get_data()
            for device in devices.values():
                last_update = self.update_datetime.get(device.hwid, None)
                if last_update is None:
                    self.update_flag[device.hwid] = True
                    LOGGER.debug(
                        "Update required for HWID %s: previous value = None, current value = %s",
                        device.hwid,
                        device.currentMeteringAt,
                    )
                else:
                    if last_update != device.currentMeteringAt:
                        self.update_flag[device.hwid] = True
                        LOGGER.debug(
                            "Update required for HWID %s: previous value = %s, current value = %s",
                            device.hwid,
                            last_update,
                            device.currentMeteringAt,
                        )
                    else:
                        self.update_flag[device.hwid] = False
                        LOGGER.debug(
                            "No update required for HWID %s: previous value = %s, current value = %s",
                            device.hwid,
                            last_update,
                            device.currentMeteringAt,
                        )

                self.update_datetime[device.hwid] = device.currentMeteringAt

            return devices
        except FoxInsightsApiAuthenticationError as exception:
            LOGGER.error(exception)
            raise ConfigEntryAuthFailed(exception) from exception
        except FoxInsightsApiConnectionError as exception:
            LOGGER.warning(exception)
            raise UpdateFailed(exception) from exception
        except FoxInsightsApiError as exception:
            LOGGER.exception(exception)
            raise UpdateFailed(exception) from exception

    def needs_update(self, device: FoxInsightsDevice) -> bool:
        """Return if values should be updated."""
        return self.update_flag.get(device.hwid, False)

    def get_data(self, device: FoxInsightsDevice) -> FoxInsightsDevice | None:
        """Return the data for a device."""
        return self.data.get(device.hwid, None)

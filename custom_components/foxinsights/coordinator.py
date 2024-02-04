"""DataUpdateCoordinator for FoxInsights."""

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

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
    """The coordinator responsible for updating and managing the data for FoxInsights devices."""

    def __init__(self, hass: HomeAssistant, api: FoxInsightsApi) -> None:
        """Initialize the object."""
        self.api = api
        self.update_datetime: dict[str, str] = {}
        self.update_flag: dict[str, bool] = {}
        self.unavailable: bool = False

        super().__init__(
            hass, LOGGER, name=DOMAIN, update_interval=timedelta(minutes=15)
        )

    async def _async_update_data(self) -> dict[str, FoxInsightsDevice]:
        """Update the data for all devices. Does not raise exceptions because otherwise all sensor states are set to "unavailable".

        :return: a dictionary mapping the hardware IDs of the devices to the corresponding FoxInsightsDevice objects.
        """
        self.unavailable = False

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
            # raise ConfigEntryAuthFailed(exception) from exception
        except FoxInsightsApiConnectionError as exception:
            LOGGER.warning(exception)
            # raise UpdateFailed(exception) from exception
        except FoxInsightsApiError as exception:
            LOGGER.warning(exception)
            # raise UpdateFailed(exception) from exception
        except Exception as exception:  # pylint: disable=broad-except
            LOGGER.exception(exception)
            # raise UpdateFailed(exception) from exception

        self.unavailable = True
        return {}

    def is_unavailable(self) -> bool:
        """Check if the data is unavailable.

        :return: True if the data is unavailable, False otherwise.
        """
        return self.unavailable

    def needs_update(self, device: FoxInsightsDevice) -> bool:
        """Check if the given device needs an update.

        :param device: The device to check for an update.
        :return: True if the device needs an update, False otherwise.
        """
        return not self.unavailable and self.update_flag.get(device.hwid, False)

    def get_data(self, device: FoxInsightsDevice) -> FoxInsightsDevice | None:
        """Return the data for a device.

        :param device: The device for which to retrieve data.
        :return: The data associated with the device if found, otherwise None.
        """
        if self.unavailable:
            return None

        return self.data.get(device.hwid, None)

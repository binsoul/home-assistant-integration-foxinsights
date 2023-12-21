"""Custom integration to integrate FoxInsights with Home Assistant.

For more details about this integration, please refer to
https://github.com/binsoul/home-assistant-integration-foxinsights
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import FoxInsightsApi
from .const import CONF_EMAIL, CONF_PASSWORD, DOMAIN
from .coordinator import FoxInsightsDataUpdateCoordinator

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration."""
    hass.data.setdefault(DOMAIN, {})

    data_update_coordinator = FoxInsightsDataUpdateCoordinator(
        hass,
        FoxInsightsApi(
            entry.data[CONF_EMAIL],
            entry.data[CONF_PASSWORD],
            async_get_clientsession(hass),
        ),
    )

    hass.data[DOMAIN][entry.entry_id] = data_update_coordinator

    await data_update_coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    if len(hass.data[DOMAIN]) == 0:
        hass.data.pop(DOMAIN)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

"""Config flow for FoxInsights integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    FoxInsightsApi,
    FoxInsightsApiAuthenticationError,
    FoxInsightsApiConnectionError,
    FoxInsightsApiError,
)
from .const import CONF_EMAIL, CONF_PASSWORD, DOMAIN, LOGGER, NAME


class FoxInsightsConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for FoxInsights."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        errors = {}

        if user_input is not None:
            api = FoxInsightsApi(
                user_input[CONF_EMAIL],
                user_input[CONF_PASSWORD],
                async_get_clientsession(self.hass),
            )

            try:
                await api.async_test_login()
            except FoxInsightsApiAuthenticationError as exception:
                LOGGER.error(exception)
                errors["base"] = "auth"
            except FoxInsightsApiConnectionError as exception:
                LOGGER.warning(exception)
                errors["base"] = "connection"
            except FoxInsightsApiError as exception:
                LOGGER.exception(exception)
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(
                    NAME + "-" + user_input[CONF_EMAIL.lower()]
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input[CONF_EMAIL],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_EMAIL,
                        default=(user_input or {}).get(CONF_EMAIL),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    ),
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD
                        ),
                    ),
                }
            ),
            errors=errors,
        )

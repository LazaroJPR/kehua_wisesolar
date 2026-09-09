"""Config flow for Kehua WiseSolar integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_PASSWORD, CONF_STATION_ID, CONF_USERNAME, DOMAIN
from .wisesolar_api import WiseSolarApiClient

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Kehua WiseSolar."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            username = user_input[CONF_USERNAME].strip()
            password = user_input[CONF_PASSWORD]
            station_id = user_input.get(CONF_STATION_ID)
            if station_id:
                station_id = str(station_id).strip()

            await self.async_set_unique_id(f"kehua_wisesolar_{username}")
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            client = WiseSolarApiClient(session, username, password, station_id)

            try:
                await client.async_login()
                data = await client.async_get_data()
                plant_name = data.get("station_name") or f"Kehua Solar ({username})"
                user_input[CONF_STATION_ID] = client.station_id

                return self.async_create_entry(title=plant_name, data=user_input)
            except ValueError as err:
                _LOGGER.warning("WiseSolar auth failed: %s", err)
                errors["base"] = "invalid_auth"
            except Exception as err:
                _LOGGER.exception("Unexpected error during WiseSolar setup: %s", err)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Optional(CONF_STATION_ID): str,
                }
            ),
            errors=errors,
        )

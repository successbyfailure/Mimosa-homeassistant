"""Config flow for Mimosa integration."""
from __future__ import annotations

from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.util import slugify

from .api import (
    MimosaApi,
    MimosaApiError,
    MimosaAuthError,
    MimosaFeatureDisabled,
    MimosaServiceUnavailable,
)
from .const import (
    CONF_API_TOKEN,
    CONF_BASE_URL,
    CONF_CLIENT_ID,
    CONF_ENABLE_FIREWALL_RULES,
    CONF_ENABLE_HEATMAP,
    CONF_ENABLE_RULES,
    CONF_ENABLE_SIGNALS,
    CONF_HEATMAP_INTERVAL,
    CONF_HEATMAP_LIMIT,
    CONF_HEATMAP_SOURCE,
    CONF_HEATMAP_WINDOW,
    CONF_RULES_INTERVAL,
    CONF_SIGNALS_INTERVAL,
    CONF_STATS_INTERVAL,
    DEFAULT_HEATMAP_INTERVAL,
    DEFAULT_HEATMAP_LIMIT,
    DEFAULT_HEATMAP_SOURCE,
    DEFAULT_HEATMAP_WINDOW,
    DEFAULT_ENABLE_FIREWALL_RULES,
    DEFAULT_ENABLE_HEATMAP,
    DEFAULT_ENABLE_RULES,
    DEFAULT_ENABLE_SIGNALS,
    DEFAULT_NAME,
    DEFAULT_RULES_INTERVAL,
    DEFAULT_SIGNALS_INTERVAL,
    DEFAULT_STATS_INTERVAL,
    DOMAIN,
)


async def _validate(
    hass: HomeAssistant, base_url: str, api_token: str
) -> None:
    api = MimosaApi(hass=hass, base_url=base_url, api_token=api_token)
    try:
        await api.fetch_stats()
    except MimosaAuthError as err:
        raise err
    except (MimosaFeatureDisabled, MimosaServiceUnavailable):
        return
    except MimosaApiError as err:
        raise err


class MimosaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mimosa."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        errors: Dict[str, str] = {}

        if user_input is not None:
            base_url = user_input[CONF_BASE_URL].strip().rstrip("/")
            api_token = user_input[CONF_API_TOKEN].strip()
            client_id = user_input.get(CONF_CLIENT_ID) or "homeassistant"
            name = user_input.get(CONF_NAME) or DEFAULT_NAME

            await self.async_set_unique_id(slugify(base_url))
            self._abort_if_unique_id_configured()

            try:
                await _validate(self.hass, base_url, api_token)
            except MimosaAuthError:
                errors["base"] = "invalid_auth"
            except MimosaApiError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_NAME: name,
                        CONF_BASE_URL: base_url,
                        CONF_API_TOKEN: api_token,
                        CONF_CLIENT_ID: client_id,
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_BASE_URL): str,
                vol.Required(CONF_API_TOKEN): str,
                vol.Optional(CONF_CLIENT_ID, default="homeassistant"): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        return MimosaOptionsFlow(config_entry)


class MimosaOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Mimosa."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        data_schema = vol.Schema(
            {
                vol.Optional(CONF_CLIENT_ID, default=options.get(CONF_CLIENT_ID, "homeassistant")): str,
                vol.Optional(CONF_STATS_INTERVAL, default=options.get(CONF_STATS_INTERVAL, DEFAULT_STATS_INTERVAL)): int,
                vol.Optional(CONF_SIGNALS_INTERVAL, default=options.get(CONF_SIGNALS_INTERVAL, DEFAULT_SIGNALS_INTERVAL)): int,
                vol.Optional(CONF_HEATMAP_INTERVAL, default=options.get(CONF_HEATMAP_INTERVAL, DEFAULT_HEATMAP_INTERVAL)): int,
                vol.Optional(CONF_RULES_INTERVAL, default=options.get(CONF_RULES_INTERVAL, DEFAULT_RULES_INTERVAL)): int,
                vol.Optional(CONF_ENABLE_SIGNALS, default=options.get(CONF_ENABLE_SIGNALS, DEFAULT_ENABLE_SIGNALS)): bool,
                vol.Optional(CONF_ENABLE_HEATMAP, default=options.get(CONF_ENABLE_HEATMAP, DEFAULT_ENABLE_HEATMAP)): bool,
                vol.Optional(CONF_ENABLE_RULES, default=options.get(CONF_ENABLE_RULES, DEFAULT_ENABLE_RULES)): bool,
                vol.Optional(CONF_ENABLE_FIREWALL_RULES, default=options.get(CONF_ENABLE_FIREWALL_RULES, DEFAULT_ENABLE_FIREWALL_RULES)): bool,
                vol.Optional(CONF_HEATMAP_SOURCE, default=options.get(CONF_HEATMAP_SOURCE, DEFAULT_HEATMAP_SOURCE)): str,
                vol.Optional(CONF_HEATMAP_WINDOW, default=options.get(CONF_HEATMAP_WINDOW, DEFAULT_HEATMAP_WINDOW)): str,
                vol.Optional(CONF_HEATMAP_LIMIT, default=options.get(CONF_HEATMAP_LIMIT, DEFAULT_HEATMAP_LIMIT)): int,
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema)

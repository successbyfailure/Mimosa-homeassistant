"""Mimosa integration for Home Assistant."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import MimosaApi
from .const import (
    CONF_API_TOKEN,
    CONF_BASE_URL,
    CONF_CLIENT_ID,
    CONF_HEATMAP_INTERVAL,
    CONF_HEATMAP_LIMIT,
    CONF_HEATMAP_SOURCE,
    CONF_HEATMAP_WINDOW,
    CONF_RULES_INTERVAL,
    CONF_SIGNALS_INTERVAL,
    CONF_STATS_INTERVAL,
    CONF_ENABLE_HEATMAP,
    CONF_ENABLE_SIGNALS,
    CONF_ENABLE_RULES,
    CONF_ENABLE_FIREWALL_RULES,
    DEFAULT_HEATMAP_INTERVAL,
    DEFAULT_HEATMAP_LIMIT,
    DEFAULT_HEATMAP_SOURCE,
    DEFAULT_HEATMAP_WINDOW,
    DEFAULT_ENABLE_FIREWALL_RULES,
    DEFAULT_ENABLE_HEATMAP,
    DEFAULT_ENABLE_RULES,
    DEFAULT_ENABLE_SIGNALS,
    DEFAULT_RULES_INTERVAL,
    DEFAULT_SIGNALS_INTERVAL,
    DEFAULT_STATS_INTERVAL,
    DOMAIN,
)
from .coordinator import (
    MimosaFirewallRulesCoordinator,
    MimosaHeatmapCoordinator,
    MimosaRulesCoordinator,
    MimosaSignalsCoordinator,
    MimosaStatsCoordinator,
)

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.SWITCH]


@dataclass
class MimosaRuntime:
    api: MimosaApi
    stats_coordinator: MimosaStatsCoordinator
    signals_coordinator: Optional[MimosaSignalsCoordinator]
    heatmap_coordinator: Optional[MimosaHeatmapCoordinator]
    rules_coordinator: Optional[MimosaRulesCoordinator]
    firewall_rules_coordinator: Optional[MimosaFirewallRulesCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    base_url = entry.data[CONF_BASE_URL]
    api_token = entry.data[CONF_API_TOKEN]
    api = MimosaApi(hass=hass, base_url=base_url, api_token=api_token)

    options = entry.options
    stats_interval = options.get(CONF_STATS_INTERVAL, DEFAULT_STATS_INTERVAL)
    signals_interval = options.get(CONF_SIGNALS_INTERVAL, DEFAULT_SIGNALS_INTERVAL)
    heatmap_interval = options.get(CONF_HEATMAP_INTERVAL, DEFAULT_HEATMAP_INTERVAL)
    rules_interval = options.get(CONF_RULES_INTERVAL, DEFAULT_RULES_INTERVAL)
    heatmap_window = options.get(CONF_HEATMAP_WINDOW, DEFAULT_HEATMAP_WINDOW)
    heatmap_source = options.get(CONF_HEATMAP_SOURCE, DEFAULT_HEATMAP_SOURCE)
    heatmap_limit = options.get(CONF_HEATMAP_LIMIT, DEFAULT_HEATMAP_LIMIT)

    enable_signals = options.get(CONF_ENABLE_SIGNALS, DEFAULT_ENABLE_SIGNALS)
    enable_heatmap = options.get(CONF_ENABLE_HEATMAP, DEFAULT_ENABLE_HEATMAP)
    enable_rules = options.get(CONF_ENABLE_RULES, DEFAULT_ENABLE_RULES)
    enable_firewall_rules = options.get(
        CONF_ENABLE_FIREWALL_RULES, DEFAULT_ENABLE_FIREWALL_RULES
    )

    stats_coordinator = MimosaStatsCoordinator(hass, api, stats_interval)
    await stats_coordinator.async_config_entry_first_refresh()

    signals_coordinator = None
    if enable_signals:
        client_id = options.get(CONF_CLIENT_ID, entry.data.get(CONF_CLIENT_ID, "homeassistant"))
        signals_coordinator = MimosaSignalsCoordinator(
            hass, api, signals_interval, client_id
        )
        await signals_coordinator.async_config_entry_first_refresh()

    heatmap_coordinator = None
    if enable_heatmap:
        heatmap_coordinator = MimosaHeatmapCoordinator(
            hass,
            api,
            heatmap_interval,
            window=heatmap_window,
            limit=heatmap_limit,
            source=heatmap_source,
        )
        await heatmap_coordinator.async_config_entry_first_refresh()

    rules_coordinator = None
    if enable_rules:
        rules_coordinator = MimosaRulesCoordinator(hass, api, rules_interval)
        await rules_coordinator.async_config_entry_first_refresh()

    firewall_rules_coordinator = None
    if enable_firewall_rules:
        firewall_rules_coordinator = MimosaFirewallRulesCoordinator(
            hass, api, rules_interval, config_id=None
        )
        await firewall_rules_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = MimosaRuntime(
        api=api,
        stats_coordinator=stats_coordinator,
        signals_coordinator=signals_coordinator,
        heatmap_coordinator=heatmap_coordinator,
        rules_coordinator=rules_coordinator,
        firewall_rules_coordinator=firewall_rules_coordinator,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_options))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def _async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)

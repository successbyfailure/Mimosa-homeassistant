"""Coordinators for Mimosa integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any, Dict, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    MimosaApi,
    MimosaApiError,
    MimosaAuthError,
    MimosaFeatureDisabled,
    MimosaServiceUnavailable,
)

_LOGGER = logging.getLogger(__name__)


class MimosaStatsCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Coordinator for Mimosa stats."""

    def __init__(self, hass: HomeAssistant, api: MimosaApi, interval: int) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name="mimosa_stats",
            update_interval=timedelta(seconds=interval),
        )
        self.api = api

    async def _async_update_data(self) -> Dict[str, Any]:
        try:
            return await self.api.fetch_stats()
        except MimosaAuthError as err:
            raise UpdateFailed(f"Auth error: {err}") from err
        except (MimosaFeatureDisabled, MimosaServiceUnavailable, MimosaApiError) as err:
            raise UpdateFailed(f"Stats error: {err}") from err


class MimosaSignalsCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Coordinator for Mimosa signals."""

    def __init__(self, hass: HomeAssistant, api: MimosaApi, interval: int, client_id: str) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name="mimosa_signals",
            update_interval=timedelta(seconds=interval),
        )
        self.api = api
        self.client_id = client_id

    async def _async_update_data(self) -> Dict[str, Any]:
        try:
            return await self.api.fetch_signals(self.client_id)
        except MimosaAuthError as err:
            raise UpdateFailed(f"Auth error: {err}") from err
        except (MimosaFeatureDisabled, MimosaServiceUnavailable, MimosaApiError) as err:
            raise UpdateFailed(f"Signals error: {err}") from err


class MimosaHeatmapCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Coordinator for Mimosa heatmap."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: MimosaApi,
        interval: int,
        *,
        window: str,
        limit: int,
        source: str,
    ) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name="mimosa_heatmap",
            update_interval=timedelta(seconds=interval),
        )
        self.api = api
        self.window = window
        self.limit = limit
        self.source = source

    async def _async_update_data(self) -> Dict[str, Any]:
        try:
            return await self.api.fetch_heatmap(
                window=self.window, limit=self.limit, source=self.source
            )
        except MimosaAuthError as err:
            raise UpdateFailed(f"Auth error: {err}") from err
        except (MimosaFeatureDisabled, MimosaServiceUnavailable, MimosaApiError) as err:
            raise UpdateFailed(f"Heatmap error: {err}") from err


class MimosaRulesCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Coordinator for Mimosa rules."""

    def __init__(self, hass: HomeAssistant, api: MimosaApi, interval: int) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name="mimosa_rules",
            update_interval=timedelta(seconds=interval),
        )
        self.api = api

    async def _async_update_data(self) -> Dict[str, Any]:
        try:
            return await self.api.fetch_rules()
        except MimosaAuthError as err:
            raise UpdateFailed(f"Auth error: {err}") from err
        except (MimosaFeatureDisabled, MimosaServiceUnavailable, MimosaApiError) as err:
            raise UpdateFailed(f"Rules error: {err}") from err


class MimosaFirewallRulesCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Coordinator for Mimosa firewall rules."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: MimosaApi,
        interval: int,
        config_id: Optional[str],
    ) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name="mimosa_firewall_rules",
            update_interval=timedelta(seconds=interval),
        )
        self.api = api
        self.config_id = config_id

    async def _async_update_data(self) -> Dict[str, Any]:
        try:
            return await self.api.fetch_firewall_rules(self.config_id)
        except MimosaAuthError as err:
            raise UpdateFailed(f"Auth error: {err}") from err
        except (MimosaFeatureDisabled, MimosaServiceUnavailable, MimosaApiError) as err:
            raise UpdateFailed(f"Firewall rules error: {err}") from err

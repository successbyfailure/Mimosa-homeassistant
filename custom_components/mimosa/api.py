"""API client for Mimosa."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import async_timeout
from aiohttp import ClientError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession


class MimosaApiError(Exception):
    """Base error for Mimosa API."""


class MimosaAuthError(MimosaApiError):
    """Auth error for Mimosa API."""


class MimosaFeatureDisabled(MimosaApiError):
    """Raised when a feature is disabled in Mimosa."""


class MimosaServiceUnavailable(MimosaApiError):
    """Raised when Mimosa reports service unavailable."""


@dataclass
class MimosaApi:
    """Async client for Mimosa API."""

    hass: HomeAssistant
    base_url: str
    api_token: str
    timeout: int = 10

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = f"{self.base_url.rstrip('/')}{path}"
        session = async_get_clientsession(self.hass)
        try:
            async with async_timeout.timeout(self.timeout):
                async with session.request(
                    method, url, headers=self._headers, params=params
                ) as resp:
                    if resp.status == 401:
                        raise MimosaAuthError("Unauthorized")
                    if resp.status == 403:
                        raise MimosaFeatureDisabled("Feature disabled")
                    if resp.status == 503:
                        raise MimosaServiceUnavailable("Service unavailable")
                    if resp.status >= 400:
                        text = await resp.text()
                        raise MimosaApiError(f"HTTP {resp.status}: {text}")
                    if resp.status == 204:
                        return {}
                    return await resp.json()
        except ClientError as err:
            raise MimosaApiError(str(err)) from err

    async def fetch_stats(self) -> Dict[str, Any]:
        return await self._request("GET", "/api/homeassistant/stats")

    async def fetch_signals(self, client_id: str) -> Dict[str, Any]:
        return await self._request(
            "GET", "/api/homeassistant/signals", params={"client_id": client_id}
        )

    async def fetch_heatmap(
        self, *, window: str, limit: int, source: str
    ) -> Dict[str, Any]:
        return await self._request(
            "GET",
            "/api/homeassistant/heatmap",
            params={"window": window, "limit": limit, "source": source},
        )

    async def fetch_rules(self) -> Dict[str, Any]:
        return await self._request("GET", "/api/homeassistant/rules")

    async def toggle_rule(self, rule_id: int, enabled: bool) -> Dict[str, Any]:
        return await self._request(
            "POST",
            f"/api/homeassistant/rules/{rule_id}/toggle",
            params={"enabled": str(enabled).lower()},
        )

    async def fetch_firewall_rules(self, config_id: Optional[str] = None) -> Dict[str, Any]:
        params = {}
        if config_id:
            params["config_id"] = config_id
        return await self._request(
            "GET", "/api/homeassistant/firewall/rules", params=params
        )

    async def toggle_firewall_rule(
        self, rule_uuid: str, enabled: bool, config_id: Optional[str] = None
    ) -> Dict[str, Any]:
        params = {"enabled": str(enabled).lower()}
        if config_id:
            params["config_id"] = config_id
        return await self._request(
            "POST",
            f"/api/homeassistant/firewall/rules/{rule_uuid}/toggle",
            params=params,
        )

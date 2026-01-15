"""Switch entities for Mimosa rules."""
from __future__ import annotations

from typing import Any, Dict, Optional

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_NAME, DEFAULT_NAME, DOMAIN
from .coordinator import MimosaFirewallRulesCoordinator, MimosaRulesCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    runtime = hass.data[DOMAIN][entry.entry_id]

    if runtime.rules_coordinator:
        _setup_dynamic_rules(runtime.rules_coordinator, entry, async_add_entities)

    if runtime.firewall_rules_coordinator:
        _setup_dynamic_firewall(
            runtime.firewall_rules_coordinator, entry, async_add_entities
        )


def _setup_dynamic_rules(
    coordinator: MimosaRulesCoordinator, entry: ConfigEntry, async_add_entities
) -> None:
    known: set[int] = set()

    def _refresh() -> None:
        data = coordinator.data or {}
        rules = data.get("rules", [])
        new_entities: list[SwitchEntity] = []
        for rule in rules:
            rule_id = rule.get("id")
            if rule_id is None or rule_id in known:
                continue
            known.add(rule_id)
            new_entities.append(MimosaRuleSwitch(coordinator, entry, rule_id))
        if new_entities:
            async_add_entities(new_entities)

    _refresh()
    coordinator.async_add_listener(_refresh)


def _setup_dynamic_firewall(
    coordinator: MimosaFirewallRulesCoordinator, entry: ConfigEntry, async_add_entities
) -> None:
    known: set[str] = set()

    def _refresh() -> None:
        data = coordinator.data or {}
        rules = data.get("rules", [])
        new_entities: list[SwitchEntity] = []
        for rule in rules:
            rule_uuid = _resolve_firewall_rule_uuid(rule)
            if not rule_uuid or rule_uuid in known:
                continue
            known.add(rule_uuid)
            new_entities.append(MimosaFirewallRuleSwitch(coordinator, entry, rule_uuid))
        if new_entities:
            async_add_entities(new_entities)

    _refresh()
    coordinator.async_add_listener(_refresh)


def _resolve_firewall_rule_uuid(rule: Dict[str, Any]) -> Optional[str]:
    return (
        rule.get("uuid")
        or rule.get("rule_uuid")
        or rule.get("id")
        or rule.get("rule_id")
    )


class MimosaRuleSwitch(CoordinatorEntity[MimosaRulesCoordinator], SwitchEntity):
    """Switch for Mimosa offense rules."""

    def __init__(
        self, coordinator: MimosaRulesCoordinator, entry: ConfigEntry, rule_id: int
    ) -> None:
        super().__init__(coordinator)
        self.rule_id = rule_id
        self._attr_unique_id = f"{entry.entry_id}_rule_{rule_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data.get(CONF_NAME, DEFAULT_NAME),
            manufacturer="Mimosa",
        )

    @property
    def _rule(self) -> Dict[str, Any]:
        data = self.coordinator.data or {}
        rules = data.get("rules", [])
        for rule in rules:
            if rule.get("id") == self.rule_id:
                return rule
        return {}

    @property
    def name(self) -> str | None:
        rule = self._rule
        description = rule.get("description") or "Rule"
        return f"Mimosa Rule {self.rule_id} - {description}"

    @property
    def is_on(self) -> bool | None:
        return bool(self._rule.get("enabled", False))

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        rule = self._rule
        return {
            "plugin": rule.get("plugin"),
            "event_id": rule.get("event_id"),
            "severity": rule.get("severity"),
            "description": rule.get("description"),
            "min_last_hour": rule.get("min_last_hour"),
            "min_total": rule.get("min_total"),
            "min_blocks_total": rule.get("min_blocks_total"),
            "block_minutes": rule.get("block_minutes"),
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.api.toggle_rule(self.rule_id, True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.api.toggle_rule(self.rule_id, False)
        await self.coordinator.async_request_refresh()


class MimosaFirewallRuleSwitch(
    CoordinatorEntity[MimosaFirewallRulesCoordinator], SwitchEntity
):
    """Switch for firewall rules."""

    def __init__(
        self,
        coordinator: MimosaFirewallRulesCoordinator,
        entry: ConfigEntry,
        rule_uuid: str,
    ) -> None:
        super().__init__(coordinator)
        self.rule_uuid = rule_uuid
        self._attr_unique_id = f"{entry.entry_id}_firewall_rule_{rule_uuid}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data.get(CONF_NAME, DEFAULT_NAME),
            manufacturer="Mimosa",
        )

    @property
    def _rule(self) -> Dict[str, Any]:
        data = self.coordinator.data or {}
        rules = data.get("rules", [])
        for rule in rules:
            if _resolve_firewall_rule_uuid(rule) == self.rule_uuid:
                return rule
        return {}

    @property
    def name(self) -> str | None:
        rule = self._rule
        label = rule.get("name") or rule.get("description") or self.rule_uuid
        return f"Firewall Rule {label}"

    @property
    def is_on(self) -> bool | None:
        rule = self._rule
        if "enabled" in rule:
            return bool(rule.get("enabled"))
        if "is_enabled" in rule:
            return bool(rule.get("is_enabled"))
        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        rule = self._rule
        if not rule:
            return {}
        payload = dict(rule)
        payload["rule_uuid"] = self.rule_uuid
        return payload

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.api.toggle_firewall_rule(
            self.rule_uuid, True, self.coordinator.config_id
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.api.toggle_firewall_rule(
            self.rule_uuid, False, self.coordinator.config_id
        )
        await self.coordinator.async_request_refresh()

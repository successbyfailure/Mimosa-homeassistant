"""Binary sensors for Mimosa signals."""
from __future__ import annotations

from typing import Any, Dict

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_NAME, DEFAULT_NAME, DOMAIN
from .coordinator import MimosaSignalsCoordinator


SIGNAL_TYPES = (
    ("offense", "Mimosa Offense Signal"),
    ("block", "Mimosa Block Signal"),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    runtime = hass.data[DOMAIN][entry.entry_id]
    coordinator = runtime.signals_coordinator
    if not coordinator:
        return

    entities = [
        MimosaSignalBinarySensor(coordinator, entry, key, name)
        for key, name in SIGNAL_TYPES
    ]
    async_add_entities(entities)


class MimosaSignalBinarySensor(
    CoordinatorEntity[MimosaSignalsCoordinator], BinarySensorEntity
):
    """Binary sensor for Mimosa signals."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(
        self,
        coordinator: MimosaSignalsCoordinator,
        entry: ConfigEntry,
        signal_key: str,
        name: str,
    ) -> None:
        super().__init__(coordinator)
        self._signal_key = signal_key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_signal_{signal_key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data.get(CONF_NAME, DEFAULT_NAME),
            manufacturer="Mimosa",
        )

    @property
    def is_on(self) -> bool | None:
        data = self.coordinator.data or {}
        signal = data.get(self._signal_key) or {}
        return bool(signal.get("new")) if signal else False

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        data = self.coordinator.data or {}
        signal = data.get(self._signal_key) or {}
        return {
            "new_count": signal.get("new_count"),
            "last_id": signal.get("last_id"),
            "last": signal.get("last"),
            "timestamp": data.get("timestamp"),
        }

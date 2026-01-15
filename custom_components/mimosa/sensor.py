"""Sensors for Mimosa."""
from __future__ import annotations

from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_NAME, DOMAIN, DEFAULT_NAME
from .coordinator import MimosaHeatmapCoordinator, MimosaStatsCoordinator


STAT_SENSORS: tuple[tuple[str, str, str], ...] = (
    ("offenses.total", "Offenses Total", "mdi:alert"),
    ("offenses.last_24h", "Offenses 24h", "mdi:alert"),
    ("offenses.last_7d", "Offenses 7d", "mdi:alert"),
    ("offenses.last_1h", "Offenses 1h", "mdi:alert"),
    ("blocks.current", "Blocks Current", "mdi:shield"),
    ("blocks.total", "Blocks Total", "mdi:shield"),
    ("blocks.last_24h", "Blocks 24h", "mdi:shield"),
    ("blocks.last_7d", "Blocks 7d", "mdi:shield"),
    ("blocks.last_1h", "Blocks 1h", "mdi:shield"),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    runtime = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [
        MimosaStatsSensor(runtime.stats_coordinator, entry, key, name, icon)
        for key, name, icon in STAT_SENSORS
    ]

    if runtime.heatmap_coordinator:
        entities.append(MimosaHeatmapSensor(runtime.heatmap_coordinator, entry))

    async_add_entities(entities)


class MimosaStatsSensor(CoordinatorEntity[MimosaStatsCoordinator], SensorEntity):
    """Sensor for Mimosa stats."""

    def __init__(
        self,
        coordinator: MimosaStatsCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        icon: str,
    ) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_icon = icon
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data.get(CONF_NAME, DEFAULT_NAME),
            manufacturer="Mimosa",
        )

    @property
    def native_value(self) -> Optional[int]:
        data = self.coordinator.data or {}
        parts = self._key.split(".")
        cursor: Any = data
        for part in parts:
            if not isinstance(cursor, dict):
                return None
            cursor = cursor.get(part)
        if cursor is None:
            return None
        try:
            return int(cursor)
        except (TypeError, ValueError):
            return None


class MimosaHeatmapSensor(
    CoordinatorEntity[MimosaHeatmapCoordinator], SensorEntity
):
    """Sensor for Mimosa heatmap metadata."""

    _attr_name = "Mimosa Heatmap Points"
    _attr_icon = "mdi:map"

    def __init__(self, coordinator: MimosaHeatmapCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_heatmap_points"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data.get(CONF_NAME, DEFAULT_NAME),
            manufacturer="Mimosa",
        )

    @property
    def native_value(self) -> Optional[int]:
        data = self.coordinator.data or {}
        count = data.get("points_count")
        try:
            return int(count)
        except (TypeError, ValueError):
            return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        data = self.coordinator.data or {}
        return {
            "window": data.get("window"),
            "points": data.get("points", []),
            "total_profiles": data.get("total_profiles"),
            "points_count": data.get("points_count"),
            "source": getattr(self.coordinator, "source", None),
        }

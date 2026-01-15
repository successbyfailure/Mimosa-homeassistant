"""Constants for the Mimosa integration."""
from __future__ import annotations

DOMAIN = "mimosa"

CONF_BASE_URL = "base_url"
CONF_API_TOKEN = "api_token"
CONF_CLIENT_ID = "client_id"
CONF_NAME = "name"

CONF_STATS_INTERVAL = "stats_interval"
CONF_SIGNALS_INTERVAL = "signals_interval"
CONF_HEATMAP_INTERVAL = "heatmap_interval"
CONF_RULES_INTERVAL = "rules_interval"
CONF_HEATMAP_WINDOW = "heatmap_window"
CONF_HEATMAP_SOURCE = "heatmap_source"
CONF_HEATMAP_LIMIT = "heatmap_limit"
CONF_ENABLE_SIGNALS = "enable_signals"
CONF_ENABLE_HEATMAP = "enable_heatmap"
CONF_ENABLE_RULES = "enable_rules"
CONF_ENABLE_FIREWALL_RULES = "enable_firewall_rules"

DEFAULT_NAME = "Mimosa"
DEFAULT_STATS_INTERVAL = 60
DEFAULT_SIGNALS_INTERVAL = 30
DEFAULT_HEATMAP_INTERVAL = 300
DEFAULT_RULES_INTERVAL = 120
DEFAULT_HEATMAP_WINDOW = "24h"
DEFAULT_HEATMAP_SOURCE = "offenses"
DEFAULT_HEATMAP_LIMIT = 300

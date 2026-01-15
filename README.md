# Mimosa Home Assistant Integration

Custom component for Home Assistant that connects to Mimosa and exposes:

- Stats sensors (offenses/blocks).
- Signals as binary sensors (offense/block).
- Heatmap metadata sensor.
- Rule switches (Mimosa and firewall rules).

## Installation (manual)

1. Copy `custom_components/mimosa` into your Home Assistant config directory.
2. Restart Home Assistant.
3. Go to Settings -> Devices & Services -> Add Integration -> Mimosa.

## Configuration

You need a Mimosa base URL and API token (from Mimosa Settings -> Home Assistant).
Enable the Home Assistant integration in Mimosa before connecting.

## Options

After setup, you can tune polling intervals and enable/disable features in the
integration options.

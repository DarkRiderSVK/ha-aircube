# Ubiquiti airCube for Home Assistant

Custom Home Assistant integration for Ubiquiti airCube devices using the local ubus API.

This integration allows monitoring and control of supported airCube devices directly from Home Assistant without any cloud dependency.

---

# Features

## Sensors

- Connected clients
- Signal strength
- Noise level
- Site score
- Firmware version
- Uptime
- Quality information

## Switches

- LED control
- PoE Passthrough
- 2.4GHz WiFi
- 5GHz WiFi (AC models only)
- Guest WiFi networks

## Device Tracker

- Connected wireless clients

---

# Supported Devices

Tested on:

- airCube ISP
- airCube AC

Other airCube models may also work.

---

# Installation

## HACS (Recommended)

1. Open HACS
2. Go to Integrations
3. Click the 3 dots in the top right
4. Select `Custom repositories`
5. Add this repository URL:

```text
https://github.com/DarkRiderSVK/ha-aircube
```

6. Category: `Integration`
7. Install `Ubiquiti airCube`
8. Restart Home Assistant

---

## Manual Installation

Copy the `custom_components/aircube` folder into:

```text
/config/custom_components/
```

Then restart Home Assistant.

---

# Configuration

1. Open Home Assistant
2. Go to:

```text
Settings → Devices & Services
```

3. Click:

```text
Add Integration
```

4. Search for:

```text
Ubiquiti airCube
```

5. Enter:

- Host / IP address
- Username
- Password

---

# Notes

## airCube ISP

The airCube ISP model only supports 2.4GHz WiFi.

The integration automatically hides 5GHz controls for ISP models.

## LED Control

airCube uses unusual LED logic internally:

- `0 = enabled`
- `1 = disabled`

The integration automatically handles this internally.

---

# Local API

This integration communicates directly with the device using:

- HTTPS
- ubus RPC API

No cloud services are used.

---

# Known Limitations

- Self-signed SSL certificates are ignored
- Some firmware versions may behave differently
- Ubiquiti internally exposes disabled features on some models

---

# Screenshots

## Home Assistant Device

- Sensors
- WiFi controls
- PoE control
- LED control

---

# Development

Repository:

```text
https://github.com/DarkRiderSVK/ha-aircube
```

Issues and pull requests are welcome.

---

# License

MIT License

---

# Author

Created by:

```text
DarkRiderSVK
```
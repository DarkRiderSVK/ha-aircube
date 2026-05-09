from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        AirCubeConnectedClientsSensor(coordinator),
        AirCubeNoiseSensor(coordinator),
        AirCubeSiteScoreSensor(coordinator),
        AirCubeUptimeSensor(coordinator),
        AirCubeFirmwareSensor(coordinator),
        AirCubeSignalSensor(coordinator),
        AirCubeQualitySensor(coordinator),
    ]

    wireless = coordinator.data.get("wireless", {}).get("interface", {})

    for iface in wireless.values():
        for client in iface.get("assoclist", []):
            mac = client.get("mac")

            entities.append(AirCubeClientSignalSensor(coordinator, mac))
            entities.append(AirCubeClientNoiseSensor(coordinator, mac))
            entities.append(AirCubeClientTxRateSensor(coordinator, mac))
            entities.append(AirCubeClientRxRateSensor(coordinator, mac))

    async_add_entities(entities)


class AirCubeBaseSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def mac(self):
        return (
            self.coordinator.data
            .get("system", {})
            .get("board", {})
            .get("macaddr", "unknown")
            .replace(":", "")
            .lower()
        )

    @property
    def device_info(self):
        board = (
            self.coordinator.data
            .get("system", {})
            .get("board", {})
        )

        firmware = (
            self.coordinator.data
            .get("ubnt", {})
            .get("fwupdate", {})
            .get("local", "unknown")
        )

        return DeviceInfo(
            identifiers={(DOMAIN, self.mac)},
            name=board.get("hostname", "airCube"),
            manufacturer="Ubiquiti",
            model=board.get("model", "airCube"),
            sw_version=firmware,
        )


class AirCubeConnectedClientsSensor(AirCubeBaseSensor):
    _attr_name = "airCube Connected Clients"
    _attr_icon = "mdi:wifi"

    @property
    def unique_id(self):
        return f"{self.mac}_connected_clients"

    @property
    def state(self):
        total = 0

        wireless = self.coordinator.data.get("wireless", {}).get("interface", {})

        for iface in wireless.values():
            total += len(iface.get("assoclist", []))

        return total


class AirCubeNoiseSensor(AirCubeBaseSensor):
    _attr_name = "airCube Noise"
    _attr_native_unit_of_measurement = "dBm"
    _attr_icon = "mdi:signal"

    @property
    def unique_id(self):
        return f"{self.mac}_noise"

    @property
    def state(self):
        try:
            return (
                self.coordinator.data["wireless"]["interface"]["wlan0"]["info"]["noise"]
            )
        except Exception:
            return None


class AirCubeSiteScoreSensor(AirCubeBaseSensor):
    _attr_name = "airCube Site Score"
    _attr_native_unit_of_measurement = "%"
    _attr_icon = "mdi:wifi-strength-4"

    @property
    def unique_id(self):
        return f"{self.mac}_site_score"

    @property
    def state(self):
        try:
            return self.coordinator.data["wireless"]["site_score"]
        except Exception:
            return None


class AirCubeUptimeSensor(AirCubeBaseSensor):
    _attr_name = "airCube Uptime"
    _attr_native_unit_of_measurement = "s"
    _attr_icon = "mdi:clock-outline"

    @property
    def unique_id(self):
        return f"{self.mac}_uptime"

    @property
    def state(self):
        try:
            return self.coordinator.data["system"]["info"]["uptime"]
        except Exception:
            return None


class AirCubeFirmwareSensor(AirCubeBaseSensor):
    _attr_name = "airCube Firmware"
    _attr_icon = "mdi:update"

    @property
    def unique_id(self):
        return f"{self.mac}_firmware"

    @property
    def state(self):
        try:
            return self.coordinator.data["ubnt"]["fwupdate"]["local"]
        except Exception:
            return None


class AirCubeSignalSensor(AirCubeBaseSensor):
    _attr_name = "airCube Signal"
    _attr_native_unit_of_measurement = "dBm"
    _attr_icon = "mdi:wifi"

    @property
    def unique_id(self):
        return f"{self.mac}_signal"

    @property
    def state(self):
        try:
            return (
                self.coordinator.data["wireless"]["interface"]["wlan0"]["info"]["signal"]
            )
        except Exception:
            return None


class AirCubeQualitySensor(AirCubeBaseSensor):
    _attr_name = "airCube Quality"
    _attr_native_unit_of_measurement = "%"
    _attr_icon = "mdi:wifi-strength-3"

    @property
    def unique_id(self):
        return f"{self.mac}_quality"

    @property
    def state(self):
        try:
            return (
                self.coordinator.data["wireless"]["interface"]["wlan0"]["info"]["quality"]
            )
        except Exception:
            return None
            
class AirCubeClientSignalSensor(AirCubeBaseSensor):
    def __init__(self, coordinator, client_mac):
        super().__init__(coordinator)

        self.client_mac = client_mac

    @property
    def unique_id(self):
        return f"{self.client_mac}_signal"

    @property
    def name(self):
        return f"Client {self.client_mac} Signal"

    @property
    def native_unit_of_measurement(self):
        return "dBm"

    @property
    def icon(self):
        return "mdi:wifi"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, f"client_{self.client_mac}")},
        )

    @property
    def state(self):
        wireless = self.coordinator.data.get("wireless", {}).get("interface", {})

        for iface in wireless.values():
            for client in iface.get("assoclist", []):
                if client.get("mac") == self.client_mac:
                    return client.get("signal")

        return None


class AirCubeClientNoiseSensor(AirCubeBaseSensor):
    def __init__(self, coordinator, client_mac):
        super().__init__(coordinator)

        self.client_mac = client_mac

    @property
    def unique_id(self):
        return f"{self.client_mac}_noise"

    @property
    def name(self):
        return f"Client {self.client_mac} Noise"

    @property
    def native_unit_of_measurement(self):
        return "dBm"

    @property
    def icon(self):
        return "mdi:signal"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, f"client_{self.client_mac}")},
        )

    @property
    def state(self):
        wireless = self.coordinator.data.get("wireless", {}).get("interface", {})

        for iface in wireless.values():
            for client in iface.get("assoclist", []):
                if client.get("mac") == self.client_mac:
                    return client.get("noise")

        return None


class AirCubeClientTxRateSensor(AirCubeBaseSensor):
    def __init__(self, coordinator, client_mac):
        super().__init__(coordinator)

        self.client_mac = client_mac

    @property
    def unique_id(self):
        return f"{self.client_mac}_tx"

    @property
    def name(self):
        return f"Client {self.client_mac} TX Rate"

    @property
    def native_unit_of_measurement(self):
        return "Mbps"

    @property
    def icon(self):
        return "mdi:upload"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, f"client_{self.client_mac}")},
        )

    @property
    def state(self):
        wireless = self.coordinator.data.get("wireless", {}).get("interface", {})
    
        for iface in wireless.values():
            for client in iface.get("assoclist", []):
                if client.get("mac") == self.client_mac:
    
                    rate = client.get("tx", {}).get("rate")
    
                    if rate is not None:
                        return round(rate / 1000, 1)
    
        return None


class AirCubeClientRxRateSensor(AirCubeBaseSensor):
    def __init__(self, coordinator, client_mac):
        super().__init__(coordinator)

        self.client_mac = client_mac

    @property
    def unique_id(self):
        return f"{self.client_mac}_rx"

    @property
    def name(self):
        return f"Client {self.client_mac} RX Rate"

    @property
    def native_unit_of_measurement(self):
        return "Mbps"

    @property
    def icon(self):
        return "mdi:download"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, f"client_{self.client_mac}")},
        )

    @property
    def state(self):
        wireless = self.coordinator.data.get("wireless", {}).get("interface", {})
    
        for iface in wireless.values():
            for client in iface.get("assoclist", []):
                if client.get("mac") == self.client_mac:
    
                    rate = client.get("rx", {}).get("rate")
    
                    if rate is not None:
                        return round(rate / 1000, 1)
    
        return None
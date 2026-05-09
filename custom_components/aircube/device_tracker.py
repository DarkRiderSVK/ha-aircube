from homeassistant.components.device_tracker import SourceType
from homeassistant.components.device_tracker.config_entry import ScannerEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    wireless = coordinator.data.get("wireless", {}).get("interface", {})

    for iface_name, iface_data in wireless.items():
        assoclist = iface_data.get("assoclist", [])

        for client in assoclist:
            entities.append(
                AirCubeClientTracker(
                    coordinator,
                    iface_name,
                    client,
                )
            )

    async_add_entities(entities)


class AirCubeClientTracker(CoordinatorEntity, ScannerEntity):
    def __init__(self, coordinator, iface_name, client):
        super().__init__(coordinator)

        self.iface_name = iface_name
        self.client_mac = client.get("mac", "unknown")

    @property
    def unique_id(self):
        return f"aircube_client_{self.client_mac.lower().replace(':', '')}"

    @property
    def name(self):
        return f"Client {self.client_mac}"

    @property
    def source_type(self):
        return SourceType.ROUTER

    @property
    def mac_address(self):
        return self.client_mac

    @property
    def ip_address(self):
        return None

    @property
    def device_info(self):
        board = (
            self.coordinator.data
            .get("system", {})
            .get("board", {})
        )

        parent_mac = (
            board.get("macaddr", "unknown")
            .replace(":", "")
            .lower()
        )

        return DeviceInfo(
            identifiers={(DOMAIN, f"client_{self.client_mac}")},
            name=f"Client {self.client_mac}",
            manufacturer="WiFi Client",
            model="Wireless Device",
            via_device=(DOMAIN, parent_mac),
        )

    @property
    def is_connected(self):
        wireless = self.coordinator.data.get("wireless", {}).get("interface", {})
        iface = wireless.get(self.iface_name, {})

        assoclist = iface.get("assoclist", [])

        for client in assoclist:
            if client.get("mac") == self.client_mac:
                return True

        return False

    @property
    def extra_state_attributes(self):
        wireless = self.coordinator.data.get("wireless", {}).get("interface", {})
        iface = wireless.get(self.iface_name, {})

        assoclist = iface.get("assoclist", [])

        for client in assoclist:
            if client.get("mac") == self.client_mac:
                return {
                    "signal": client.get("signal"),
                    "noise": client.get("noise"),
                    "inactive": client.get("inactive"),
                    "tx_rate": client.get("tx", {}).get("rate"),
                    "rx_rate": client.get("rx", {}).get("rate"),
                    "interface": self.iface_name,
                }

        return {}
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    board = (
        coordinator.data
        .get("system", {})
        .get("board", {})
    )

    model = board.get("model", "").lower()

    entities = [
        AirCubeLedSwitch(coordinator),
        AirCubePoESwitch(coordinator),

        AirCubeRadioSwitch(
            coordinator,
            "radio0",
            "2.4GHz WiFi",
        ),

        AirCubeGuestSwitch(
            coordinator,
            "guest0",
            "Guest 2.4GHz",
        ),
    ]

    # ISP model nemá 5GHz
    if "isp" not in model:
        entities.extend([
            AirCubeRadioSwitch(
                coordinator,
                "radio1",
                "5GHz WiFi",
            ),

            AirCubeGuestSwitch(
                coordinator,
                "guest1",
                "Guest 5GHz",
            ),
        ])

    async_add_entities(entities)


class AirCubeBaseSwitch(CoordinatorEntity, SwitchEntity):
    _should_poll = False

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


class AirCubeLedSwitch(AirCubeBaseSwitch):
    _attr_icon = "mdi:led-on"
    
    async def async_added_to_hass(self):
        await self.async_update()

    @property
    def unique_id(self):
        return f"{self.mac}_led"

    @property
    def name(self):
        return "LED"

    @property
    def is_on(self):
        return getattr(self, "_state", False)

    async def async_update(self):
        values = await self.coordinator.api.uci_get(
            "led",
            "night",
        )

        enable = values.get("enable", 1)

        # normalize airCube bullshit 🤡
        enable = str(enable).lower()
        
        self._state = enable in [
            "0",
            "false",
            "off",
        ]

    async def async_turn_on(self, **kwargs):
        await self.coordinator.api.set_led(True)
        await self.async_update()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.api.set_led(False)
        await self.async_update()
        self.async_write_ha_state()


class AirCubePoESwitch(AirCubeBaseSwitch):
    _attr_icon = "mdi:flash"

    async def async_added_to_hass(self):
        await self.async_update()

    @property
    def unique_id(self):
        return f"{self.mac}_poe"

    @property
    def name(self):
        return "PoE Passthrough"

    @property
    def is_on(self):
        return getattr(self, "_state", False)

    async def async_update(self):
        values = await self.coordinator.api.uci_get(
            "ubnt",
            "hwctl",
        )

        poe = values.get("poe_pass", False)

        # normalize airCube bullshit 🤡
        poe = str(poe).lower()

        self._state = poe in [
            "1",
            "true",
            "on",
        ]

    async def async_turn_on(self, **kwargs):
        await self.coordinator.api.set_poe(True)

        await self.async_update()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.api.set_poe(False)

        await self.async_update()
        self.async_write_ha_state()

class AirCubeRadioSwitch(AirCubeBaseSwitch):
    def __init__(self, coordinator, radio, name):
        super().__init__(coordinator)

        self.radio = radio
        self._name = name

    async def async_added_to_hass(self):
        await self.async_update()

    @property
    def unique_id(self):
        return f"{self.mac}_{self.radio}"

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return getattr(self, "_state", False)

    async def async_update(self):
        values = await self.coordinator.api.uci_get(
            "wireless",
            self.radio,
        )

        disabled = values.get("disabled", False)

        self._state = str(disabled).lower() not in [
            "1",
            "true",
        ]

    async def async_turn_on(self, **kwargs):
        await self.coordinator.api.set_radio(
            self.radio,
            True,
        )

        await self.async_update()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.api.set_radio(
            self.radio,
            False,
        )

        await self.async_update()
        self.async_write_ha_state()


class AirCubeGuestSwitch(AirCubeBaseSwitch):
    def __init__(self, coordinator, guest, name):
        super().__init__(coordinator)

        self.guest = guest
        self._name = name

    async def async_added_to_hass(self):
        await self.async_update()

    @property
    def unique_id(self):
        return f"{self.mac}_{self.guest}"

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return getattr(self, "_state", False)

    async def async_update(self):
        values = await self.coordinator.api.uci_get(
            "wireless",
            self.guest,
        )

        disabled = values.get("disabled", False)

        self._state = str(disabled).lower() not in [
            "1",
            "true",
        ]

    async def async_turn_on(self, **kwargs):
        await self.coordinator.api.set_guest(
            self.guest,
            True,
        )

        await self.async_update()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.api.set_guest(
            self.guest,
            False,
        )

        await self.async_update()
        self.async_write_ha_state()
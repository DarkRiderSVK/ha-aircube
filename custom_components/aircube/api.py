import asyncio
import aiohttp


class AirCubeApi:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.token = None

    @property
    def url(self):
        return f"https://{self.host}/ubus"

    async def login(self):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": [
                "00000000000000000000000000000000",
                "session",
                "login",
                {
                    "username": self.username,
                    "password": self.password,
                },
            ],
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url,
                json=payload,
                ssl=False,
            ) as response:
                data = await response.json()

        self.token = data["result"][1]["ubus_rpc_session"]

    async def ubus_call(self, namespace, command, params):
        if not self.token:
            await self.login()

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": [
                self.token,
                namespace,
                command,
                params,
            ],
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url,
                json=payload,
                ssl=False,
            ) as response:
                data = await response.json()

        if "error" in data:
            await self.login()
            return await self.ubus_call(namespace, command, params)

        return data

    async def get_stats(self):
        data = await self.ubus_call(
            "ubnt",
            "stats",
            {},
        )

        return data["result"][1]["results"]

    async def async_get_stats(self):
        return await self.get_stats()

    async def uci_get(self, config, section):
        data = await self.ubus_call(
            "uci",
            "get",
            {
                "config": config,
                "section": section,
            },
        )

        return data["result"][1]["values"]

    async def uci_set(self, config, section, values):
        await self.ubus_call(
            "uci",
            "set",
            {
                "config": config,
                "section": section,
                "values": values,
            },
        )

        await self.ubus_call(
            "uci",
            "commit",
            {
                "config": config,
            },
        )

        await self.ubus_call(
            "uci",
            "apply",
            {
                "rollback": False,
            },
        )

        # airCube potrebuje chvíľu na apply
        await asyncio.sleep(2)

    async def set_led(self, enabled):
        if enabled:
            values = {
                "enable": 0,
                "start": 1320,
                "end": 480,
            }
        else:
            values = {
                "enable": 1,
                "start": 0,
                "end": 0,
            }
    
        await self.uci_set(
            "led",
            "night",
            values,
        )

    async def set_poe(self, enabled):
        await self.uci_set(
            "ubnt",
            "hwctl",
            {
                "poe_pass": enabled,
            },
        )

    async def set_radio(self, radio, enabled):
        await self.uci_set(
            "wireless",
            radio,
            {
                "disabled": not enabled,
            },
        )

    async def set_guest(self, guest, enabled):
        await self.uci_set(
            "wireless",
            guest,
            {
                "disabled": not enabled,
            },
        )
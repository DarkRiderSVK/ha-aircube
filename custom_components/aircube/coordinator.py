from datetime import timedelta
import logging

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import AirCubeApi
from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class AirCubeCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, host, username, password):
        self.api = AirCubeApi(host, username, password)

        super().__init__(
            hass,
            logger=_LOGGER,
            name="aircube",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        try:
            return await self.api.async_get_stats()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with airCube: {err}") from err
"""Coordinate data for powerview devices."""
from __future__ import annotations

from datetime import timedelta
import logging

from aiopvapi.shades import Shades
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import SHADE_DATA
from .shade_data import PowerviewShadeData

_LOGGER = logging.getLogger(__name__)


class PowerviewShadeUpdateCoordinator(DataUpdateCoordinator[PowerviewShadeData]):
    """DataUpdateCoordinator to gather data from a powerview hub."""

    def __init__(
        self,
        hass: HomeAssistant,
        shades: Shades,
        hub_address: str,
    ) -> None:
        """Initialize DataUpdateCoordinator to gather data for specific SmartPlug."""
        self.shades = shades
        super().__init__(
            hass,
            _LOGGER,
            name=f"powerview hub {hub_address}",
            update_interval=timedelta(seconds=60),
        )

    async def _async_update_data(self) -> PowerviewShadeData:
        """Fetch data from shade endpoint."""
        async with async_timeout.timeout(10):
            shade_entries = await self.shades.get_resources()
        if not shade_entries:
            raise UpdateFailed("Failed to fetch new shade data")
        self.data.store_group_data(shade_entries[SHADE_DATA])
        return self.data

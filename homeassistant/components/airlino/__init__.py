"""The airlino integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS, Platform
from homeassistant.core import HomeAssistant

from .airlino import AirlinoEntity
from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.MEDIA_PLAYER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up airlino from a config entry."""
    # Instance of AirlinoEntity class, that manages the communication is stored
    print(entry.data)

    entity = AirlinoEntity(hass, entry.data[CONF_IP_ADDRESS])
    if await entity.update_data():
        # Entries are lodaded from config when created or started
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entity

        # Create HA object for MEDIA_PLAYER Platform
        hass.config_entries.async_setup_platforms(entry, PLATFORMS)

        return True

    # Return false if reached to this point (Not yet returned above)
    return False


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    print("unloading entry")
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

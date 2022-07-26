"""Media player class for airlino."""

from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN as AIRLINO_DOMAIN

SUPPORTED_FEATURES = (
    MediaPlayerEntityFeature.GROUPING
    | MediaPlayerEntityFeature.NEXT_TRACK
    | MediaPlayerEntityFeature.PAUSE
    | MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.PLAY_MEDIA
    | MediaPlayerEntityFeature.PREVIOUS_TRACK
    | MediaPlayerEntityFeature.SELECT_SOURCE
    | MediaPlayerEntityFeature.STOP
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.VOLUME_STEP
)

SUPPORTED_SOUND_MODES = ["Stereo [L/R]", "Left [L/L]", "Right [R/R", "Mono"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Media player is set up based on a config entry."""
    print(hass.data[AIRLINO_DOMAIN])
    players = hass.data[AIRLINO_DOMAIN]
    devices = [AirlinoMediaPlayer(player) for player in players.values()]
    async_add_entities(devices, True)


class AirlinoMediaPlayer(MediaPlayerEntity):
    """Media player class for airlino entity."""

    def __init__(self, player):
        """Create AirlinoMediaPlayer object."""
        self._attr_device_class = MediaPlayerDeviceClass.RECEIVER
        self._attr_supported_features = SUPPORTED_FEATURES
        self._player = player
        self._unique_id = player.mac
        self._name = player.name
        print("Media Player __init__ triggered")

    async def async_play_media(
        self, media_type: str, media_id: str, **kwargs: Any
    ) -> None:
        """Play a piece of media."""

    def select_source(self, source):
        """Select input source."""
        print("Method for selecting source triggered")
        print(source)

    # async def async_get_browse_image(self, media_content_type, media_content_id, media_image_id=None):
    #    """Serve album art. Returns (content, content_type)."""
    #    print("Request for album art triggered")
    #    image_url = ...
    #    return await self._async_fetch_image(image_url)

    async def async_join_players(self, group_members):
        """Join `group_members` as a player group with the current player."""
        print("Join player To play together with this player")
        print(group_members)

    async def async_unjoin_player(self):
        """Remove this player from any group."""
        print("Unjoin this player from possible group")

    async def async_update(self):
        """Update supported features of the player."""
        await self._player.update()
        print("Player update triggered")

    async def async_media_next_track(self):
        """Play next track."""
        print("Next track triggered")

    async def async_media_previous_track(self):
        """Play previous track."""
        print("Prev track triggered")

    async def async_media_pause(self):
        """Send pause command."""
        print("Pause triggered")

    async def async_media_play(self):
        """Send play command."""
        print("Play triggered")

    async def async_media_stop(self):
        """Stop media."""
        print("Stop triggered")

    async def async_mute_volume(self, mute):
        """Mute volume."""
        self._player.mute = mute

    async def async_set_volume_level(self, volume):
        """Set volume."""
        print("Set volume: ")
        print(volume)

    async def async_volume_down(self):
        """Decrease volume."""
        print("Decrease volume")

    async def async_volume_up(self):
        """Increase volume."""
        print("Increase volume")

    @property
    def available(self) -> bool:
        """Property GETTER for available state."""
        return True

    @property
    def supported_features(self) -> int:
        """Property GETTER for supported features."""
        return self._attr_supported_features

    @property
    def media_content_type(self):
        """Content type of current playing media."""

    @property
    def name(self) -> str:
        """Name of the entity."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Property GETTER for unique id."""
        return self._unique_id

    @property
    def sound_mode(self) -> str:
        """Property GETTER for sound mode."""
        # TBD check current mode when updated and provide for returning here
        return "Stereo [L/R]"

    @property
    def sound_mode_list(self) -> list:
        """Property GETTER for sound mode list."""
        # TBD check current mode when updated and provide for returning here
        return SUPPORTED_SOUND_MODES

    @property
    def source(self) -> str:
        """Return current source."""
        return "Radio"

    @property
    def source_list(self) -> list:
        """Return source list."""
        return ["Radio"]

    @property
    def media_image_url(self) -> str:
        """Property GETTER for album art url."""
        return self._player.album_art_url

    @property
    def media_image_remotely_accessible(self) -> bool:
        """Property GETTER for info if media player image is accessible remotely (from outside of the network)."""
        return True

    @property
    def device_class(self) -> str:
        """Property GETTER for device class."""
        return str(self._attr_device_class)

    @property
    def group_members(self) -> list:
        """Property GETTER for list of group member (if any)."""
        return self._player.group_members

    @property
    def is_on(self) -> bool:
        """Property GETTER for is_on state."""
        return self._player.is_on

    @property
    def media_title(self) -> str:
        """Property GETTER for media title."""
        return self._player.media_title

    @property
    def state(self) -> str:
        """Property GETTER for device state."""
        return self._player.state

    @property
    def is_volume_muted(self) -> bool:
        """Property GETTER for mute state."""
        return self._player.mute

"""Support for airlino devices."""

from requests import Response, exceptions, post

from homeassistant.const import STATE_IDLE
from homeassistant.core import HomeAssistant

from .const import SW_API_MAPPING


class AirlinoEntity:
    """Entity class of airlino device."""

    def __init__(self, hass: HomeAssistant, ip_address: str) -> None:
        """Create AirlinoEntity object."""
        self._hass = hass
        self._ip_address = ip_address
        # Trigger API to get name
        self._name = ""
        self._mac = ""
        self._api_version = 11
        self._mute = False
        self._state = STATE_IDLE
        self._album_art_url = ""
        self._media_title = None
        self._is_on = False
        self._group_members = [""]

    async def update(self):
        """Update info for entity."""
        self._album_art_url = "https://cdn.prod.www.spiegel.de/images/ac728c48-0001-0004-0000-000001304585_w360_r1.0084033613445378_fpx53.34_fpy53.79.jpg"

        # Media title:
        # Radio active: now playing from station
        # TIDAL active: track

    async def update_data(self) -> bool:
        """Update data and return if device is proper airlino device."""
        try:
            await self.__check_api_version()
            response_device__action = await connect_handler(
                self._hass,
                self.ip_address,
                self._api_version,
                "device.action",
                {"action": "info"},
            )

            response_network_action = await connect_handler(
                self._hass,
                self.ip_address,
                self._api_version,
                "network.action",
                {"action": "info"},
            )
        except ConnectionError:
            return False
        else:
            # device action check
            if "devicename" in response_device__action.json():
                self._name = response_device__action.json()["devicename"]
            else:
                return False

            # network action check
            if "wlan" in response_network_action.json():
                self._mac = response_network_action.json()["wlan"]["mac"]
            elif "eth" in response_network_action.json():
                self._mac = response_network_action.json()["eth"]["mac"]
            else:
                return False

        return True

    async def __check_api_version(self):
        """Check api version supported by device."""

        # Info from documentation

        response = {}

        try:
            response = await connect_handler(
                self._hass, self.ip_address, 10, "device.action", {"action": "info"}
            )
        except IncompleteResponse:
            raise ConnectionError from None
        else:
            if "firmware" in response.json():
                # Get SW version from device in list with separate entry for major, minor and patch
                separated = (response.json()["firmware"]).split(".")
                # Merge to one int for easier compare
                device_version = (
                    (int(separated[0]) * 100)
                    + (int(separated[1]) * 10)
                    + (int(separated[2]))
                )

                # List of keys for comparing with configured device
                key_list = list(SW_API_MAPPING)

                # variable for storing version if found in list
                found_api = None

                # Iterate over last index-1
                for i in range(0, len(SW_API_MAPPING) - 2, 1):
                    # list of major,minor and patch version from current and next entry
                    separated_check_curr = (key_list[i]).split(".")
                    separated_check_next = (key_list[i + 1]).split(".")

                    # Merged int from current and next entry of list to compare with configured device
                    check_version_curr = (
                        (int(separated_check_curr[0]) * 100)
                        + (int(separated_check_curr[1]) * 10)
                        + (int(separated_check_curr[2]))
                    )
                    check_version_next = (
                        (int(separated_check_next[0]) * 100)
                        + (int(separated_check_next[1]) * 10)
                        + (int(separated_check_next[2]))
                    )

                    # Configured entry is between current and next entry
                    if check_version_curr <= device_version < check_version_next:
                        found_api = list(SW_API_MAPPING.values())[i]

                # Get list of major, minor and patch from 1st key in the list and merge to int
                separated_check_first = (key_list[0]).split(".")
                check_version_first = (
                    (int(separated_check_first[0]) * 100)
                    + (int(separated_check_first[1]) * 10)
                    + (int(separated_check_first[2]))
                )
                # SW Version of configured device is smaller than 1st entry
                if device_version < check_version_first:
                    found_api = list(SW_API_MAPPING.values())[0]

                # Get list of major, minor and patch from last key in the list and merge to int
                separated_check_last = (key_list[len(SW_API_MAPPING) - 1]).split(".")
                check_version_last = (
                    (int(separated_check_last[0]) * 100)
                    + (int(separated_check_last[1]) * 10)
                    + (int(separated_check_last[2]))
                )
                # SW Version of configured device is greater or equal than last entry
                if device_version >= check_version_last:
                    found_api = list(SW_API_MAPPING.values())[len(SW_API_MAPPING) - 1]

                # if correct API version was found, store info
                if found_api is not None:
                    self._api_version = found_api
                # Nothing was found, use fallback version
                else:
                    self._api_version = 10

            # Nothing was found, use fallback version
            else:
                # Fallback value
                self._api_version = 10

    @property
    def ip_address(self) -> str:
        """Property GETTER for ip address."""
        return self._ip_address

    @property
    def name(self) -> str:
        """Property GETTER for device name."""
        return self._name

    @property
    def mac(self) -> str:
        """Property GETTER for mac address."""
        return self._mac

    @property
    def mute(self) -> bool:
        """Property GETTER for mute state."""
        return self._mute

    @mute.setter
    def mute(self, mute: bool):
        """Property SETTER for mute state."""
        self._mute = mute

    @property
    def state(self) -> str:
        """Property GETTER for device info (IDLE, PAUSED, PLAYING, STANDBY, ...)."""
        return self._state

    @property
    def album_art_url(self) -> str:
        """Property GETTER for album cover."""
        return self._album_art_url

    @property
    def media_title(self):
        """Property GETTER for media title."""
        return self._media_title

    @property
    def is_on(self):
        """Property GETTER for is_on state."""
        return self._is_on

    @property
    def group_members(self):
        """Property GETTER for group members (if any)."""
        return self._group_members


class ConnectionException(Exception):
    """Connection exception."""


class IncompleteResponse(LookupError):
    """Incomplete response exception."""

    def __init__(self, response):
        """Create object of IncompleteResponse class."""
        super().__init__(f"{response!r} information is incomplete")
        self.response = response


async def connect_handler(
    hass: HomeAssistant, ip_address: str, version: int, endpoint, data
) -> Response:
    """Async function to trigger POST request with given data."""
    response = await hass.async_add_executor_job(
        __connect_handler, ip_address, 10, endpoint, data
    )

    return response


def __connect_handler(ip_address: str, version: int, endpoint, data) -> Response:
    """Manage communication to device. Has to be executed using async_add_executor_job."""
    url = "http://" + ip_address + ":8989/api/v" + str(version) + "/" + endpoint

    headers = {"content-type": "application/json; charset=UTF-8"}

    response = Response()

    try:
        response = post(url, json=data, headers=headers)
    except exceptions.RequestException:
        raise ConnectionError from None

    return response


async def check_airlino_device_state(hass: HomeAssistant, ip_address: str) -> bool:
    """Check device info/state from discovered device to check if alright."""
    print("Try to get device info, to check, if proper device")

    # Check if proper device with lowest version.
    # Latest version is checked later

    try:
        response = await connect_handler(
            hass, ip_address, 10, "device.action", {"action": "info"}
        )
    except ConnectionError:
        return False
    else:
        # Check if response contains devicename and model and return True if so
        return bool("devicename" in response.json() and "model" in response.json())

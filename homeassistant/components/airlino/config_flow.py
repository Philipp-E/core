"""Config flow to configure the WLED integration."""
from __future__ import annotations

import ipaddress
from typing import Any

import voluptuous as vol

from homeassistant.components import zeroconf
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_IP_ADDRESS, CONF_MAC, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .airlino import AirlinoEntity, ConnectionException, check_airlino_device_state
from .const import DOMAIN


async def validate_input(hass: HomeAssistant, ip_address: str) -> dict[str, Any]:
    """Validate the user input and return device info."""

    device = AirlinoEntity(hass, ip_address)

    await device.update_data()

    return {
        CONF_NAME: device.name,
        CONF_IP_ADDRESS: device.ip_address,
        CONF_MAC: device.mac,
    }


class AirlinoFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a airlino config flow."""

    VERSION = 1
    # instance of discovered device
    discovered_device: AirlinoEntity

    ip: str
    name: str

    # Uncomment, when devices should be configurable
    # @staticmethod
    # @callback
    # def async_get_options_flow(config_entry: ConfigEntry) -> AirlinoOptionsFlowHandler:
    #     """Get the options flow for this handler."""
    #     return AirlinoOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by the user."""

        errors = {"base": ""}

        if user_input is not None:
            try:
                self.ip = str(user_input.get(CONF_IP_ADDRESS))
                device_state = await check_airlino_device_state(self.hass, self.ip)
                if device_state is True:
                    device_info = await validate_input(self.hass, self.ip)
                    print("Validated")
                else:
                    raise ConnectionException
            except KeyError:
                errors["base"] = "cannot_connect"

            except ConnectionException:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(device_info[CONF_MAC])

                self._abort_if_unique_id_configured(
                    updates={CONF_MAC: device_info[CONF_MAC]}
                )

                print("Create entry")

                # Create entry and return (Use mac, because ip could change and name could be changed by user)
                return self.async_create_entry(
                    title=device_info[CONF_NAME],
                    data={
                        CONF_NAME: device_info[CONF_NAME],
                        CONF_IP_ADDRESS: device_info[CONF_IP_ADDRESS],
                    },
                )

        else:
            user_input = {}

        # Nothing entered? Show form again
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_IP_ADDRESS): str}),
            errors=errors or {},
        )

    async def async_step_zeroconf(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ) -> FlowResult:
        """Handle zeroconf discovery."""

        found_address = None

        try:
            address_list = discovery_info.addresses
            for address_element in address_list:
                if ipaddress.ip_address(address_element).version == 4:
                    found_address = ipaddress.ip_address(address_element)

            device_state = await check_airlino_device_state(
                self.hass, str(found_address)
            )
            if device_state is False:
                return self.async_abort(reason="cannot_connect")

        except ConnectionException:
            return self.async_abort(reason="cannot_connect")

        except ValueError:
            return self.async_abort(reason="cannot_connect")
        else:
            self.ip = str(found_address)
            return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by zeroconf."""

        errors = {}

        try:
            device_info = await validate_input(self.hass, self.ip)
        except ConnectionException:
            errors["base"] = "cannot_connect"

        if user_input is not None:

            await self.async_set_unique_id(device_info[CONF_MAC])

            self._abort_if_unique_id_configured(
                updates={CONF_MAC: device_info[CONF_MAC]}
            )

            # Create entry and return (Use mac, because ip could change and name could be changed by user)
            return self.async_create_entry(
                title=device_info[CONF_NAME],
                data={
                    CONF_NAME: device_info[CONF_NAME],
                    CONF_IP_ADDRESS: device_info[CONF_IP_ADDRESS],
                },
            )

        # If not yet returned above, create empty user_input here
        # TBD remove if not needed
        # user_input = {}

        return self.async_show_form(
            step_id="zeroconf_confirm",
            description_placeholders={"name": device_info[CONF_NAME]},
        )


# Uncomment, when devices should be configurable
# class AirlinoOptionsFlowHandler(OptionsFlow):
#     """Handle airlino options."""

#     def __init__(self, config_entry: ConfigEntry) -> None:
#         """Initialize airlino options flow."""
#         self.config_entry = config_entry

#     async def async_step_init(
#         self, user_input: dict[str, Any] | None = None
#     ) -> FlowResult:
#         """Manage Airlino options."""
#         if user_input is not None:
#             return self.async_create_entry(title="", data=user_input)

#         return self.async_show_form(
#             step_id="init",
#             data_schema=vol.Schema(
#                 {
#                     vol.Optional(CONF_NAME,
#                     default=self.config_entry.data.get(CONF_NAME),
#                     ): str
#                 }
#             ),
#         )

"""Config flow for TickTick Integration."""

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import config_entry_oauth2_flow

from .application_credentials import regionalize_implementation
from .const import CONF_REGION, DEFAULT_REGION, DOMAIN, REGIONS


class OAuth2FlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Config flow to handle TickTick Integration OAuth2 authentication."""

    DOMAIN = DOMAIN

    def __init__(self) -> None:
        """Initialize the config flow."""
        super().__init__()
        self._region = DEFAULT_REGION

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> config_entries.ConfigFlowResult:
        """Select the service before authentication.

        Args:
            user_input: The selected service, or None when showing the form.

        Returns:
            The next configuration flow step.
        """
        if user_input is not None:
            self._region = user_input[CONF_REGION]
            return await self.async_step_pick_implementation()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_REGION, default=DEFAULT_REGION): vol.In(
                        {key: value["name"] for key, value in REGIONS.items()}
                    )
                }
            ),
        )

    async def async_generate_authorize_url(self) -> str:
        """Generate an authorize URL for the selected service."""
        self.flow_impl = regionalize_implementation(
            self.hass, self.flow_impl, self._region
        )
        return await super().async_generate_authorize_url()

    async def async_oauth_create_entry(
        self, data: dict
    ) -> config_entries.ConfigFlowResult:
        """Create an entry with the selected region.

        Args:
            data: OAuth token data and the selected credential implementation.

        Returns:
            The created config entry.
        """
        return self.async_create_entry(
            title=self.flow_impl.name,
            data={**data, CONF_REGION: self._region},
        )

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return logging.getLogger(__name__)

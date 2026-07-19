"""Application credentials platform for the TickTick Integration integration."""

from homeassistant.components.application_credentials import AuthorizationServer
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow

from .const import DEFAULT_REGION, REGIONS


class RegionalOAuth2Implementation(
    config_entry_oauth2_flow.LocalOAuth2Implementation
):
    """OAuth implementation using the endpoints for a selected region.

    The application credentials platform provides the client credentials, while
    this wrapper selects the matching authorize and token endpoints.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        implementation: config_entry_oauth2_flow.AbstractOAuth2Implementation,
        region: str,
    ) -> None:
        """Initialize the regional implementation."""
        region_config = REGIONS.get(region, REGIONS[DEFAULT_REGION])
        super().__init__(
            hass,
            implementation.domain,
            implementation.client_id,
            implementation.client_secret,
            region_config["authorize_url"],
            region_config["token_url"],
        )
        self._name = implementation.name
        self._region = region

    @property
    def name(self) -> str:
        """Return the credential name."""
        return self._name

    @property
    def region(self) -> str:
        """Return the selected region."""
        return self._region


async def async_get_authorization_server(hass: HomeAssistant) -> AuthorizationServer:
    """Return authorization server."""
    region = REGIONS[DEFAULT_REGION]
    return AuthorizationServer(
        authorize_url=region["authorize_url"],
        token_url=region["token_url"],
    )


def regionalize_implementation(
    hass: HomeAssistant,
    implementation: config_entry_oauth2_flow.AbstractOAuth2Implementation,
    region: str,
) -> RegionalOAuth2Implementation:
    """Return an OAuth implementation for the selected region."""
    if (
        isinstance(implementation, RegionalOAuth2Implementation)
        and implementation.region == region
    ):
        return implementation
    return RegionalOAuth2Implementation(hass, implementation, region)

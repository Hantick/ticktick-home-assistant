"""The TickTick Integration integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, SupportsResponse
from homeassistant.helpers import aiohttp_client, config_entry_oauth2_flow

from . import api
from .const import DOMAIN
from .service_handlers import (
    handle_complete_task,
    handle_create_task,
    handle_update_task,
    handle_delete_task,
    handle_get_projects,
    handle_get_task,
)
from .ticktick.ticktick_api import TickTickApiClient

type TickTickConfigEntry = ConfigEntry[api.AsyncConfigEntryAuth]


async def async_setup_entry(hass: HomeAssistant, entry: TickTickConfigEntry) -> bool:
    """Set up TickTick Integration from a config entry."""

    implementation = (
        await config_entry_oauth2_flow.async_get_config_entry_implementation(
            hass, entry
        )
    )

    session = config_entry_oauth2_flow.OAuth2Session(hass, entry, implementation)

    # Using an aiohttp-based API lib
    entry.runtime_data = api.AsyncConfigEntryAuth(
        aiohttp_client.async_get_clientsession(hass), session
    )

    access_token = await entry.runtime_data.async_get_access_token()
    tickTickApiClient = TickTickApiClient(entry.runtime_data._websession, access_token)  # noqa: SLF001

    await register_services(hass, tickTickApiClient)

    platforms = []  # no platforms for now, change in the future TODO
    await hass.config_entries.async_forward_entry_setups(entry, platforms)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: TickTickConfigEntry) -> bool:
    """Unload a TickTick config entry."""
    return await hass.config_entries.async_unload(entry)


async def register_services(
    hass: HomeAssistant, tickTickApiClient: TickTickApiClient
) -> None:
    """Register TickTick services."""

    hass.services.async_register(
        DOMAIN,
        "get_task",
        await handle_get_task(tickTickApiClient),
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        "create_task",
        await handle_create_task(tickTickApiClient),
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        "update_task",
        await handle_update_task(tickTickApiClient),
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        "complete_task",
        await handle_complete_task(tickTickApiClient),
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN,
        "delete_task",
        await handle_delete_task(tickTickApiClient),
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        "get_projects",
        await handle_get_projects(tickTickApiClient),
        supports_response=SupportsResponse.OPTIONAL,
    )
    # hass.services.async_register(DOMAIN, 'get_project', await handle_my_service)
    # hass.services.async_register(DOMAIN, 'get_detailed_project', handle_my_service(tickTickApiClient))
    # hass.services.async_register(DOMAIN, 'delete_project', handle_my_service(tickTickApiClient))
    # hass.services.async_register(DOMAIN, 'create_project', handle_my_service(tickTickApiClient))

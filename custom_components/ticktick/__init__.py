"""The TickTick Integration integration."""

from __future__ import annotations

import datetime
import logging

from homeassistant.components.http import async_import_module
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, SupportsResponse
from homeassistant.helpers import aiohttp_client

from . import api
from .const import DOMAIN
from .coordinator import TickTickCoordinator
from .service_handlers import (
    handle_complete_task,
    handle_create_task,
    handle_delete_task,
    handle_get_projects,
    handle_get_task,
    handle_update_task,
)
from .ticktick_api_python.ticktick_api import TickTickAPIClient

type TickTickConfigEntry = ConfigEntry[api.AsyncConfigEntryAuth]

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = datetime.timedelta(minutes=1)

PLATFORMS = [Platform.TODO]


async def async_setup_entry(hass: HomeAssistant, entry: TickTickConfigEntry) -> bool:
    """Set up TickTick Integration from a config entry."""

    config_entry_oauth2_flow = await async_import_module(
        hass, "homeassistant.helpers.config_entry_oauth2_flow"
    )

    implementation = (
        await config_entry_oauth2_flow.async_get_config_entry_implementation(
            hass, entry
        )
    )

    session = config_entry_oauth2_flow.OAuth2Session(hass, entry, implementation)

    # Using an aiohttp-based API lib
    aiohttp_session = aiohttp_client.async_get_clientsession(hass)
    entry.runtime_data = api.AsyncConfigEntryAuth(aiohttp_session, session)
    access_token = await entry.runtime_data.async_get_access_token()

    tickTickApiClient = TickTickAPIClient(access_token, aiohttp_session)

    await register_coordiantor(hass, tickTickApiClient, entry, access_token)
    await register_services(hass, tickTickApiClient)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: TickTickConfigEntry) -> bool:
    """Unload a TickTick config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def register_coordiantor(
    hass: HomeAssistant,
    tickTickApiClient: TickTickAPIClient,
    entry: TickTickConfigEntry,
    access_token: str,
) -> None:
    """Register Coordinator for TickTick Todo Entity."""
    coordinator = TickTickCoordinator(
        hass, _LOGGER, entry, SCAN_INTERVAL, tickTickApiClient, access_token
    )
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator


async def register_services(
    hass: HomeAssistant, tickTickApiClient: TickTickAPIClient
) -> None:
    """Register TickTick services."""

    hass.services.async_register(
        DOMAIN,
        "get_task",
        await handle_get_task(tickTickApiClient),
        supports_response=SupportsResponse.ONLY,
    )
    hass.services.async_register(
        DOMAIN,
        "create_task",
        await handle_create_task(tickTickApiClient),
        supports_response=SupportsResponse.ONLY,
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
        "update_task",
        await handle_update_task(tickTickApiClient),
        supports_response=SupportsResponse.OPTIONAL,
    )

    hass.services.async_register(
        DOMAIN,
        "get_projects",
        await handle_get_projects(tickTickApiClient),
        supports_response=SupportsResponse.ONLY,
    )
    # hass.services.async_register(DOMAIN, 'get_project', await handle_my_service)
    # hass.services.async_register(DOMAIN, 'get_detailed_project', handle_my_service(tickTickApiClient))
    # hass.services.async_register(DOMAIN, 'delete_project', handle_my_service(tickTickApiClient))
    # hass.services.async_register(DOMAIN, 'create_project', handle_my_service(tickTickApiClient))

"""Service Hanlders for TickTick Integration."""

from collections.abc import Awaitable, Callable
from typing import Any, Type, TypeVar

from custom_components.ticktick.ticktick.task import Task
from homeassistant.core import ServiceCall

from .const import PROJECT_ID, TASK_ID
from .ticktick.ticktick_api import TickTickApiClient


# === Task Scope ===
async def handle_get_task(client: TickTickApiClient) -> Callable:
    """Return a handler function for the 'get_task' endpoint."""
    return await _create_handler(client.get_task, PROJECT_ID, TASK_ID)


async def handle_create_task(client: TickTickApiClient) -> Callable:
    """Return a handler function for the 'create_task' endpoint."""
    return await _create_handler(client.create_task, *(Task.get_arg_names()), type=Task)


async def handle_update_task(client: TickTickApiClient) -> Callable:
    """Return a handler function for the 'update_task' endpoint."""
    return await _create_handler(client.update_task, *(Task.get_arg_names()), type=Task)


async def handle_complete_task(client: TickTickApiClient) -> Callable:
    """Return a handler function for the 'complete_task' endpoint."""
    return await _create_handler(client.complete_task, PROJECT_ID, TASK_ID)


async def handle_delete_task(client: TickTickApiClient) -> Callable:
    """Return a handler function for the 'delete_task' endpoint."""
    return await _create_handler(client.delete_task, PROJECT_ID, TASK_ID)


# === Project Scope ===
async def handle_get_projects(client: TickTickApiClient) -> Callable:
    """Return a handler function for the 'get_projects' endpoint."""
    return await _create_handler(client.get_projects)


T = TypeVar("T")


async def _create_handler(
    client_method: Callable[..., Awaitable[Any]],
    *arg_names: str,
    type: type[T] | None = None,
) -> Callable:
    """Create a reusable handler function for TickTick API endpoints."""

    async def handler(call: ServiceCall) -> dict[str, Any]:
        """Return a generic handler for TickTick API endpoints."""

        args = {arg: call.data.get(arg) for arg in arg_names}
        try:
            response = None
            if type:
                instance = type(**args)
                response = await client_method(instance)
            else:
                response = await client_method(**args)

            return {"data": response}  # noqa: TRY300
        except Exception as e:  # noqa: BLE001
            return {"error": str(e)}

    return handler

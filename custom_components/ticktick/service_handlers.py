"""Service Hanlders for TickTick Integration."""

from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any, TypeVar
from zoneinfo import ZoneInfo

from custom_components.ticktick.ticktick_api_python.models.task import Task

from homeassistant.core import ServiceCall
from homeassistant.util import dt as dt_util

from .const import PROJECT_ID, TASK_ID
from .ticktick_api_python.ticktick_api import TickTickAPIClient


# === Task Scope ===
async def handle_get_task(client: TickTickAPIClient) -> Callable:
    """Return a handler function for the 'get_task' endpoint."""
    return await _create_handler(client.get_task, PROJECT_ID, TASK_ID)


async def handle_create_task(client: TickTickAPIClient) -> Callable:
    """Return a handler function for the 'create_task' endpoint."""
    return await _create_handler(client.create_task, *(Task.get_arg_names()), type=Task)


async def handle_complete_task(client: TickTickAPIClient) -> Callable:
    """Return a handler function for the 'complete_task' endpoint."""
    return await _create_handler(client.complete_task, PROJECT_ID, TASK_ID)


async def handle_delete_task(client: TickTickAPIClient) -> Callable:
    """Return a handler function for the 'delete_task' endpoint."""
    return await _create_handler(client.delete_task, PROJECT_ID, TASK_ID)


# === Project Scope ===
async def handle_get_projects(client: TickTickAPIClient) -> Callable:
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
            if type == Task:
                if "dueDate" in args and isinstance(args["dueDate"], str):
                    args["dueDate"] = _sanitize_date(args["dueDate"], args["timeZone"])
                if "startDate" in args and isinstance(args["startDate"], str):
                    args["startDate"] = _sanitize_date(
                        args["startDate"], args["timeZone"]
                    )
                instance = type(**args)
                response = await client_method(instance, returnAsJson=True)
            else:
                response = await client_method(**args, returnAsJson=True)

            return {"data": response}  # noqa: TRY300
        except Exception as e:  # noqa: BLE001
            return {"error": str(e)}

    return handler


def _sanitize_date(date: str, timeZone: str | None) -> datetime:
    naive_dt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    if timeZone:
        zone_info = ZoneInfo(timeZone)
    else:
        zone_info = dt_util.get_default_time_zone()

    aware_dt = naive_dt.replace(tzinfo=zone_info)

    return aware_dt.strftime("%Y-%m-%dT%H:%M:%S%z")

"""TickTick API Client."""

from aiohttp import ClientResponse, ClientSession
from custom_components.ticktick.const import (
    COMPLETE_TASK,
    CREATE_TASK,
    UPDATE_TASK,
    DELETE_TASK,
    GET_PROJECTS,
    GET_TASK,
)
from custom_components.ticktick.ticktick.task import Task


class TickTickApiClient:
    """TickTick API Client."""

    def __init__(self, session: ClientSession, access_token: str) -> None:
        """Initialize the TickTick API client."""
        self._session = session
        self._headers = {"Authorization": f"Bearer {access_token}"}

    # === Task Scope ===
    async def get_task(self, projectId: str, taskId: str) -> str:
        """Return a task."""
        return await self._get(GET_TASK.format(projectId=projectId, taskId=taskId))

    async def create_task(self, task: Task) -> str:
        """Create a task."""
        json = task.toJSON()
        return await self._post(CREATE_TASK, json)

    async def update_task(self, task: Task) -> str:
        """Update a task."""
        json = task.toJSON()
        return await self._post(UPDATE_TASK.format(taskId=task.id), json)

    async def complete_task(self, projectId: str, taskId: str) -> str:
        """Complete a task."""
        return await self._post(
            COMPLETE_TASK.format(projectId=projectId, taskId=taskId)
        )

    async def delete_task(self, projectId: str, taskId: str) -> str:
        """Delete a task."""
        return await self._delete(
            DELETE_TASK.format(projectId=projectId, taskId=taskId)
        )

    # === Project Scope ===
    async def get_projects(self) -> str:
        """Return a dict of all projects basic informations."""
        return await self._get(GET_PROJECTS)

    async def _get(self, url: str) -> ClientResponse:
        response = await self._session.get(f"https://{url}", headers=self._headers)
        return await self._get_response(response)

    async def _post(self, url: str, json_body: str | None = None) -> ClientResponse:
        response = await self._session.post(
            f"https://{url}",
            headers=self._headers,
            data=json_body if json_body else None,
        )
        return await self._get_response(response)

    async def _delete(self, url: str) -> ClientResponse:
        response = await self._session.delete(f"https://{url}", headers=self._headers)
        return await self._get_response(response)

    async def _get_response(self, response: ClientResponse) -> ClientResponse:
        if response.ok:
            try:
                json_data = await response.json()
            except Exception:
                return {"status": "Success"}

            if json_data is None:  # Handle case when the response body is null
                return {"status": "Success"}
            return json_data
        return {"error": f"Unsucessful response, status code: {response.status}"}

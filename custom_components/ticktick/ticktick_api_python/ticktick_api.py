"""TickTick API Client."""

from aiohttp import ClientResponse, ClientSession
from custom_components.ticktick.const import (
    COMPLETE_TASK,
    CREATE_TASK,
    DELETE_TASK,
    GET_PROJECTS,
    GET_PROJECTS_WITH_TASKS,
    GET_TASK,
    UPDATE_TASK,
)

from .models.project import Kind, Project
from .models.project_with_tasks import ProjectWithTasks
from .models.task import Task


class TickTickAPIClient:
    """TickTick API Client."""

    def __init__(self, access_token: str, session: ClientSession) -> None:
        """Initialize the TickTick API client."""
        self._headers = {"Authorization": f"Bearer {access_token}"}
        self._session = session

    # === Task Scope ===
    async def get_task(
        self, projectId: str, taskId: str, returnAsJson: bool = False
    ) -> Task:
        """Return a task."""
        response = await self._get(GET_TASK.format(projectId=projectId, taskId=taskId))
        if returnAsJson:
            return response

        return Task.from_dict(response)

    async def create_task(self, task: Task) -> Task:
        """Create a task."""
        json = task.toJSON()
        response = await self._post(CREATE_TASK, json)
        return Task.from_dict(response)

    async def update_task(self, task: Task) -> Task:
        """Update a task."""
        json = task.toJSON()
        response = await self._post(UPDATE_TASK.format(taskId=task.id), json)
        return Task.from_dict(response)

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
    async def get_projects(self, returnAsJson: bool = False) -> list[Project]:
        """Return a dict of all projects basic informations."""
        response = await self._get(GET_PROJECTS)
        if returnAsJson:
            return response

        mappedResponse = [Project.from_dict(project) for project in response]
        filtered_projects = list(
            filter(
                lambda project: project.kind == Kind.TASK, mappedResponse
            )  # Filtering out for now Notes
        )
        return filtered_projects

    async def get_project_with_tasks(self, projectId: str) -> list[ProjectWithTasks]:
        """Return a dict of tasks for project."""
        response = await self._get(GET_PROJECTS_WITH_TASKS.format(projectId=projectId))
        return ProjectWithTasks.from_dict(response)

    async def _get(self, url: str) -> ClientResponse:
        response = await self._session.get(f"https://{url}", headers=self._headers)
        return await self._get_response(response)

    async def _post(self, url: str, json_body: str | None = None) -> ClientResponse:
        self._headers["Content-Type"] = "application/json"
        response = await self._session.post(
            f"https://{url}",
            headers=self._headers,
            data=json_body if json_body else None,
        )
        return await self._get_response(response)

    async def _delete(self, url: str) -> ClientResponse:
        response = await self._session.delete(f"https://{url}", headers=self._headers)
        return await self._get_response(response)

    async def _get_response(
        self, response: ClientResponse
    ) -> tuple[ClientResponse, bool]:
        if response.ok:
            try:
                json_data = await response.json()
            except Exception:  # noqa: BLE001
                return {"status": "Success"}

            if json_data is None:  # Handle case when the response body is null
                return {"status": "Success"}
            return json_data
        raise Exception(  # noqa: TRY002
            f"Unsucessful response from TickTick, status code: {response.status}"
        )

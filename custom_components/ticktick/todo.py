import asyncio
from typing import Any

from custom_components.ticktick.coordinator import TickTickCoordinator
from custom_components.ticktick.ticktick_api_python.models.task import Task, TaskStatus

from homeassistant.components.todo import (
    TodoItem,
    TodoItemStatus,
    TodoListEntity,
    TodoListEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the TickTick todo platform config entry."""
    coordinator: TickTickCoordinator = hass.data[DOMAIN][entry.entry_id]
    projects = await coordinator.async_get_projects()
    async_add_entities(
        TickTickTodoListEntity(coordinator, entry.entry_id, project.id, project.name)
        for project in projects
    )


def _map_task(
    item: TodoItem, projectId: str, api_task: Task | None = None
) -> tuple[Task, bool]:
    """Convert a TodoItem to Task."""
    modified = False
    if api_task:
        if item.summary != api_task.title:
            api_task.title = item.summary
            modified = True
        if item.description != api_task.content:
            api_task.content = item.description
            modified = True
        if item.due != api_task.dueDate:
            api_task.dueDate = item.due
            modified = True
        return api_task, modified
    return Task(
        projectId=projectId,
        title=item.summary,
        content=item.description,
        dueDate=item.due,
    ), modified


class TickTickTodoListEntity(CoordinatorEntity[TickTickCoordinator], TodoListEntity):
    """A TickTick TodoListEntity."""

    _attr_supported_features = (
        TodoListEntityFeature.CREATE_TODO_ITEM
        | TodoListEntityFeature.UPDATE_TODO_ITEM
        | TodoListEntityFeature.DELETE_TODO_ITEM
        | TodoListEntityFeature.SET_DUE_DATE_ON_ITEM
        | TodoListEntityFeature.SET_DUE_DATETIME_ON_ITEM
        | TodoListEntityFeature.SET_DESCRIPTION_ON_ITEM
    )

    def __init__(
        self,
        coordinator: TickTickCoordinator,
        config_entry_id: str,
        project_id: str,
        project_name: str,
    ) -> None:
        """Initialize TickTickTodoListEntity."""
        super().__init__(coordinator=coordinator)
        self._project_id = project_id
        self._attr_unique_id = f"{config_entry_id}-{project_id}"
        self._attr_name = project_name

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        projects_with_tasks = self.coordinator.data

        if projects_with_tasks is None:
            self._attr_todo_items = None
        else:
            tasks_to_add = []
            for project_with_tasks in projects_with_tasks:
                if (
                    project_with_tasks.project.id != self._project_id
                    or not project_with_tasks.tasks
                ):
                    continue

                for task in project_with_tasks.tasks:
                    tasks_to_add.append(  # noqa: PERF401
                        TodoItem(
                            uid=task.id,
                            summary=task.title,
                            status=TodoItemStatus.COMPLETED
                            if task.status == TaskStatus.COMPLETED
                            else TodoItemStatus.NEEDS_ACTION,
                            due=task.dueDate,
                            description=task.content or None,  # Don't use empty string
                        )
                    )

            if tasks_to_add:
                self._attr_todo_items = tasks_to_add

        super()._handle_coordinator_update()

    async def async_create_todo_item(self, item: TodoItem) -> None:
        """Create a To-do item."""
        if item.status != TodoItemStatus.NEEDS_ACTION:
            raise ValueError("Only active tasks may be created.")
        mapped_task, _ = _map_task(item, self._project_id)
        await self.coordinator.api.create_task(mapped_task)
        await self.coordinator.async_refresh()

    async def async_update_todo_item(self, item: TodoItem) -> None:
        """Update a To-do item."""

        async def process_status_change() -> None:
            if item.status is not None:
                # Only update status if changed
                for existing_item in self._attr_todo_items or ():
                    if existing_item.uid != item.uid:
                        continue

                    if item.status != existing_item.status:
                        if item.status == TodoItemStatus.COMPLETED:
                            await self.coordinator.api.complete_task(
                                projectId=self._project_id, taskId=item.uid
                            )
                        # else:
                        # Not supported by TickTick as they don't return completed tasks

        projects_with_tasks = self.coordinator.data
        api_task = next(
            (
                task
                for project_with_tasks in projects_with_tasks
                if project_with_tasks.tasks
                for task in project_with_tasks.tasks
                if task.id == item.uid
            ),
            None,
        )

        mapped_task, is_modified = _map_task(item, self._project_id, api_task)

        updated = False
        if is_modified:
            await self.coordinator.api.update_task(mapped_task)
            updated = True

        if not updated:
            await process_status_change()

        await self.coordinator.async_refresh()

    async def async_delete_todo_items(self, uids: list[str]) -> None:
        """Delete a To-do item."""
        await asyncio.gather(
            *[
                self.coordinator.api.delete_task(projectId=self._project_id, taskId=uid)
                for uid in uids
            ]
        )
        await self.coordinator.async_refresh()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass update state from existing coordinator data."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()

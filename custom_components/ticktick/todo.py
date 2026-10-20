import asyncio
from typing import Any
from datetime import date, datetime, time

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
from homeassistant.util import dt as dt_util

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


def _parse_ticktick_datetime(value: Any) -> datetime | None:
    """Parse a TickTick timestamp such as 2026-10-26T04:00:00.000+0000."""
    if value is None or isinstance(value, datetime):
        return value
    try:
        return datetime.strptime(str(value), "%Y-%m-%dT%H:%M:%S.%f%z")
    except ValueError:
        return dt_util.parse_datetime(str(value))


def _due_from_task(task: Task) -> date | datetime | None:
    """Return the task's due date as Home Assistant expects it.

    All-day tasks become a date in the task's time zone; others an aware datetime.
    """
    due = _parse_ticktick_datetime(task.dueDate)
    if due is None:
        return None
    if task.isAllDay:
        zone = dt_util.get_time_zone(task.timeZone) if task.timeZone else None
        return due.astimezone(zone or dt_util.get_default_time_zone()).date()
    return due


def _due_for_ticktick(due: date | datetime | None) -> tuple[datetime | None, bool]:
    """Convert a Home Assistant due value to a TickTick datetime and all-day flag.

    datetime is a subclass of date, so it must be checked first.
    """
    if isinstance(due, datetime):
        if due.tzinfo is None:
            due = due.replace(tzinfo=dt_util.get_default_time_zone())
        return due, False
    if isinstance(due, date):
        midnight = datetime.combine(due, time(), dt_util.get_default_time_zone())
        return midnight, True
    return None, False


def _map_task(
    item: TodoItem, projectId: str, api_task: Task | None = None
) -> tuple[Task, bool]:
    """Convert a TodoItem to Task."""
    modified = False
    due, all_day = _due_for_ticktick(item.due)
    if api_task:
        if (item.summary or "").strip() != (api_task.title or "").strip():
            api_task.title = item.summary
            modified = True
        if (item.description or "").strip() != (api_task.content or "").strip():
            api_task.content = item.description
            modified = True

        api_due = _parse_ticktick_datetime(api_task.dueDate)
        if due is not None and (due != api_due or all_day != bool(api_task.isAllDay)):
            # A single-day task has startDate == dueDate; keep them together so
            # moving the due date doesn't turn it into a multi-day span.
            if _parse_ticktick_datetime(api_task.startDate) == api_due:
                api_task.startDate = due
            api_task.dueDate = due
            api_task.isAllDay = all_day
            modified = True

        return api_task, modified
    return Task(
        projectId=projectId,
        title=item.summary,
        content=item.description,
        dueDate=due,
        startDate=due,
        isAllDay=all_day if due is not None else None,
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
        self._attr_todo_items = []

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
                    tasks_to_add.insert(0,  # noqa: PERF401
                        TodoItem(
                            uid=task.id,
                            summary=task.title,
                            status=TodoItemStatus.COMPLETED
                            if task.status == TaskStatus.COMPLETED
                            else TodoItemStatus.NEEDS_ACTION,
                            due=_due_from_task(task),
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

        async def process_status_change() -> bool:
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
                            return True
                        # else:
                        # Not supported by TickTick as they don't return completed tasks
            return False

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

        if await process_status_change():  # This should be changed if completing the task will support also changing description etc.
            await self.coordinator.async_refresh()
            return

        mapped_task, is_modified = _map_task(item, self._project_id, api_task)

        if is_modified:
            await self.coordinator.api.update_task(mapped_task)

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

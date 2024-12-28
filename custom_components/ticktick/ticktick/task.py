from datetime import datetime
from enum import Enum
import inspect
import json

from .check_list_item import CheckListItem, TaskStatus


class TaskPriority(Enum):
    """Enum for a Task priority."""

    NONE = 0
    LOW = 1
    MEDIUM = 3
    HIGH = 5


class Task(CheckListItem):
    """Task Class for TickTick.

    Attributes:
        items   Subtasks of Task.

    """

    def __init__(
        self,
        projectId: str,
        title: str,
        id: str | None = None,
        desc: str | None = None,
        content: str | None = None,
        priority: TaskPriority = TaskPriority.NONE,
        sortOrder: int | None = None,
        isAllDay: bool | None = None,
        ### TIME ###
        startDate: datetime | None = None,
        dueDate: datetime | None = None,
        completedTime: datetime | None = None,
        timeZone: str | None = None,  # Example "America/Los_Angeles"
        ### TIME ###
        reminders: list[str]
        | None = None,  # Example [ "TRIGGER:P0DT9H0M0S", "TRIGGER:PT0S" ]
        repeatFlag: str | None = None,  # Example "RRULE:FREQ=DAILY;INTERVAL=1"
        status: TaskStatus = TaskStatus.NORMAL,
        items: list[CheckListItem] | None = None,
    ) -> None:
        """Intialize a Task object."""
        CheckListItem.__init__(
            self,
            id,
            title,
            sortOrder,
            isAllDay,
            startDate,
            completedTime,
            timeZone,
            status,
        )
        self.projectId = projectId
        self.content = content
        self.desc = desc
        self.dueDate = dueDate
        self.items = items if items is not None else []
        self.priority = priority
        self.reminders = reminders if reminders is not None else []
        self.repeatFlag = repeatFlag

    def toJSON(self):
        """Serialize Task to json."""

        def filter_none(d):
            """Filter out None values from dictionary."""
            return {k: v for k, v in d.items() if v is not None and v != []}

        return json.dumps(filter_none(self.__dict__), sort_keys=True)

    @classmethod
    def get_arg_names(cls) -> list[str]:
        """Dynamically retrieve the names of parameters from the __init__ method for a service."""
        # Get the signature of the __init__ method
        sig = inspect.signature(cls.__init__)
        return [
            param_name
            for param_name, param in sig.parameters.items()
            if param_name != "self"
            if param_name != "id"
        ]

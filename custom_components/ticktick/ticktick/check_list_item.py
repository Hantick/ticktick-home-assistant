from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    """Enum for a Task status."""

    NORMAL = 0
    COMPLETED = 2


class CheckListItem:
    """CheckListItem class."""

    def __init__(
        self,
        id: str,
        title: str,
        sortOrder: int | None = None,
        isAllDay: bool = False,
        ### TIME ###
        startDate: datetime | None = None,
        completedTime: datetime | None = None,
        timeZone: str | None = None,  # Example "America/Los_Angeles"
        ### TIME ###
        status: TaskStatus = TaskStatus.NORMAL,
    ) -> None:
        """Intialize a CheckListItem object."""
        self.id = id
        self.title = title
        self.isAllDay = isAllDay
        self.completedTime = completedTime
        self.sortOrder = sortOrder
        self.startDate = startDate
        self.status = status
        self.timeZone = timeZone

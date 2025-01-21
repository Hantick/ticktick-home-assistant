from datetime import datetime
from enum import IntFlag


class TaskStatus(IntFlag):
    """Enum for a Task status."""

    NORMAL = 0
    COMPLETED_1 = 1
    COMPLETED_2 = 2
    COMPLETED = (
        COMPLETED_1 | COMPLETED_2
    )  # Somehow TickTick uses 1 as completed in CheckListItem and 2 in Task


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

    @staticmethod
    def from_dict(data: dict) -> "CheckListItem":
        """Create a CheckListItem instance from a dictionary."""

        return CheckListItem(
            title=data.get("title") if data.get("title") else "Unnamed SubTask",
            id=data.get("id"),
            sortOrder=data.get("sortOrder"),
            isAllDay=data.get("isAllDay"),
            startDate=data.get("startDate"),
            completedTime=data.get("completedTime"),
            timeZone=data.get("timeZone"),
            status=TaskStatus(data.get("status", TaskStatus.NORMAL.value)),
        )

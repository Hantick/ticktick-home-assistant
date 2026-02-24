from datetime import datetime, date
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

    def to_dict(self) -> dict:
        """Convert this checklist item to a JSON-ready dict."""
        def _tt_datetime(val):
            """Convert datetime/date/int/str to TickTick-compatible string."""
            if val is None:
                return None
            if isinstance(val, datetime):
                s = val.astimezone(val.tzinfo).strftime("%Y-%m-%dT%H:%M:%S%z")
            elif isinstance(val, date):
                # Convert date to datetime at midnight in local timezone
                dt = datetime(val.year, val.month, val.day)
                s = dt.astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
            elif isinstance(val, int):
                # TickTick usually uses ms timestamps
                s = datetime.fromtimestamp(val / 1000).strftime("%Y-%m-%dT%H:%M:%S%z")
            elif isinstance(val, str):
                # Assume it’s already an ISO string
                s = val
            else:
                return None

            # strip colon in timezone offset, e.g. 2025-08-29T12:00:00+10:00 → +1000
            if len(s) >= 6 and s[-3] == ":":
                s = s[:-3] + s[-2:]
            return s

        d = {
            "id": self.id,
            "title": self.title,
            "isAllDay": self.isAllDay,
            "sortOrder": self.sortOrder,
            "startDate": _tt_datetime(self.startDate),
            "completedTime": _tt_datetime(self.completedTime),
            "timeZone": self.timeZone,
            "status": int(self.status) if self.status is not None else None,
        }
        # Drop None values so TickTick accepts it
        return {k: v for k, v in d.items() if v is not None}

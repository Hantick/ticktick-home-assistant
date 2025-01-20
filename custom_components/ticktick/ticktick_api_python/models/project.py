from enum import Enum


class ViewMode(Enum):
    """Enum for a Project view mode."""

    LIST = "list"
    KANBAN = "kanban"
    TIMELINE = "timeline"


class Kind(Enum):
    """Enum for a Project kind."""

    TASK = "TASK"
    NOTE = "NOTE"


class Permission(Enum):
    """Enum for a Project permission."""

    READ = "read"
    WRITE = "write"
    COMMENT = "comment"


class Project:
    """Project Class for TickTick."""

    def __init__(
        self,
        id: str,
        groupId: str | None,
        name: str,
        color: str | None,
        sortOrder: int,
        closed: bool | None,
        viewMode: ViewMode,
        permission: Permission,
        kind: Kind = Kind.TASK,
    ) -> None:
        """Intialize a Project object."""
        self.id = id
        self.groupId = groupId
        self.name = name
        self.color = color
        self.sortOrder = sortOrder
        self.closed = closed
        self.viewMode = viewMode
        self.permission = permission
        self.kind = kind

    @staticmethod
    def from_dict(data: dict) -> "Project":
        """Create a Project instance from a dictionary."""
        return Project(
            id=data["id"],
            groupId=data.get("groupId"),
            name=data.get("name")
            if data.get("name")
            else "Unnamed Project",
            color=data.get("color"),
            sortOrder=data["sortOrder"],
            closed=data.get("closed"),
            viewMode=ViewMode(data["viewMode"])
            if data.get("viewMode")
            else None,
            permission=Permission(data["permission"])
            if data.get("permission")
            else None,
            kind=Kind(data["kind"]) if data.get("kind") else None,
        )

from .project import Project
from .task import Task


class ProjectWithTasks:
    """ProjectWithTasks Class for TickTick."""

    def __init__(
        self,
        project: Project,
        tasks: list[Task] | None,
        columns: any,  # TODO
    ) -> None:
        """Intialize a ProjectWithTasks object."""
        self.project = project
        self.tasks = tasks
        self.columns = columns

    @staticmethod
    def from_dict(data: dict) -> "ProjectWithTasks":
        """Create a ProjectWithTasks instance from a dictionary."""
        project = Project.from_dict(data["project"])
        tasks = (
            [Task.from_dict(task) for task in data.get("tasks", [])]
            if data.get("tasks")
            else None
        )
        columns = data.get(
            "columns"
        )  # TODO: Update with the appropriate logic once columns type is defined

        return ProjectWithTasks(
            project=project,
            tasks=tasks,
            columns=columns,
        )

"""Run with python3.12 -m unittest discover -s tests -v; no dependencies needed.

Home Assistant/aiohttp dependencies and integration setup/coordinator imports
are shimmed. The handlers, client, models, todo methods, and HTTP response
parsing are real; HTTP is mocked at the session boundary. This is not a full
HA integration test.
"""

from dataclasses import dataclass
from enum import Enum, IntFlag
import importlib
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch


@dataclass
class TodoItem:
    uid: str | None = None
    summary: str | None = None
    status: object = None
    due: object = None
    description: str | None = None


class TodoItemStatus(Enum):
    NEEDS_ACTION = "needs_action"
    COMPLETED = "completed"


class TodoListEntityFeature(IntFlag):
    CREATE_TODO_ITEM = 1
    DELETE_TODO_ITEM = 2
    UPDATE_TODO_ITEM = 4
    SET_DUE_DATE_ON_ITEM = 16
    SET_DUE_DATETIME_ON_ITEM = 32
    SET_DESCRIPTION_ON_ITEM = 64


class CoordinatorEntity:
    def __class_getitem__(cls, item):
        return cls

    def __init__(self, coordinator):
        self.coordinator = coordinator


def dependency_shims():
    """Bypass integration setup and supply only its external import symbols."""
    integration_path = Path(__file__).resolve().parents[1] / "custom_components"
    modules = {}

    def module(name, **attributes):
        result = ModuleType(name)
        result.__path__ = []
        result.__dict__.update(attributes)
        modules[name] = result
        return result

    module("custom_components").__path__ = [str(integration_path)]
    module("custom_components.ticktick").__path__ = [str(integration_path / "ticktick")]
    module("aiohttp", ClientResponse=object, ClientSession=object)
    module("homeassistant")
    module("homeassistant.core", ServiceCall=SimpleNamespace,
           HomeAssistant=object, callback=lambda function: function)
    module("homeassistant.util")
    dt = module("homeassistant.util.dt")
    modules["homeassistant.util"].dt = dt
    module("homeassistant.components")
    module("homeassistant.components.todo", TodoItem=TodoItem,
           TodoItemStatus=TodoItemStatus, TodoListEntity=type("TodoListEntity", (), {}),
           TodoListEntityFeature=TodoListEntityFeature)
    module("homeassistant.config_entries", ConfigEntry=object)
    module("homeassistant.helpers")
    module("homeassistant.helpers.entity_platform", AddEntitiesCallback=object)
    module("homeassistant.helpers.update_coordinator", CoordinatorEntity=CoordinatorEntity)
    module("custom_components.ticktick.coordinator", TickTickCoordinator=object)
    return modules


class ServiceResponseCompatibilityTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        # Restore sys.modules after the class, including modules loaded here.
        cls.module_patch = patch.dict(sys.modules, dependency_shims())
        cls.module_patch.start()
        cls.addClassCleanup(cls.module_patch.stop)
        cls.handlers = importlib.import_module("custom_components.ticktick.service_handlers")
        cls.client_class = importlib.import_module(
            "custom_components.ticktick.ticktick_api_python.ticktick_api"
        ).TickTickAPIClient
        cls.Task = importlib.import_module(
            "custom_components.ticktick.ticktick_api_python.models.task"
        ).Task
        cls.todo_class = importlib.import_module(
            "custom_components.ticktick.todo"
        ).TickTickTodoListEntity

    def setUp(self):
        self.response = SimpleNamespace(ok=True, json=AsyncMock())
        self.session = SimpleNamespace(
            get=AsyncMock(return_value=self.response),
            post=AsyncMock(return_value=self.response),
            delete=AsyncMock(return_value=self.response),
        )
        self.client = self.client_class("test-token", self.session)
        self.ids = {"projectId": "project-1", "taskId": "task-1"}
        self.task_data = {"projectId": "project-1", "id": "task-1",
                          "title": "Regression task", "status": 0}

    def assert_http_call(self, operation, api_base_url="https://api.ticktick.com/open/v1"):
        method = self.session.post if operation == "complete" else self.session.delete
        suffix = "/complete" if operation == "complete" else ""
        expected = {
            "headers": {"Authorization": "Bearer test-token"},
        }
        if operation == "complete":
            expected["headers"]["Content-Type"] = "application/json"
            expected["data"] = None
        method.assert_awaited_once_with(
            api_base_url + "/project/project-1/task/task-1" + suffix,
            **expected,
        )
        self.response.json.assert_awaited_once_with()

    async def test_complete_and_delete_services_reach_http_and_return_raw_data(self):
        for operation in ("complete", "delete"):
            for body in ({"status": "accepted", "extra": 1}, None, "empty"):
                with self.subTest(operation=operation, body=body):
                    self.setUp()
                    if body == "empty":
                        self.response.json.side_effect = ValueError("No JSON body")
                    else:
                        self.response.json.return_value = body
                    factory = getattr(self.handlers, f"handle_{operation}_task")
                    handler = await factory(self.client)
                    result = await handler(SimpleNamespace(data=self.ids))
                    expected = {"status": "Success"} if body in (None, "empty") else body
                    self.assertEqual(result, {"data": expected})
                    if isinstance(body, dict):
                        self.assertIs(result["data"], body)
                    self.assert_http_call(operation)

    async def test_complete_and_delete_direct_calls_preserve_response_in_all_modes(self):
        for operation in ("complete", "delete"):
            for options in ({}, {"returnAsJson": False}, {"returnAsJson": True}):
                with self.subTest(operation=operation, options=options):
                    self.setUp()
                    body = {"status": "accepted", "extra": 1}
                    self.response.json.return_value = body
                    result = await getattr(self.client, f"{operation}_task")(
                        **self.ids, **options
                    )
                    self.assertIs(result, body)
                    self.assert_http_call(operation)

    async def test_native_todo_completion_without_response_keyword(self):
        self.response.json.return_value = None
        coordinator = SimpleNamespace(api=self.client, data=[], async_refresh=AsyncMock())
        entity = self.todo_class(coordinator, "entry-1", "project-1", "Test project")
        entity._attr_todo_items = [TodoItem(uid="task-1", status=TodoItemStatus.NEEDS_ACTION)]
        await entity.async_update_todo_item(TodoItem(uid="task-1", status=TodoItemStatus.COMPLETED))
        self.assert_http_call("complete")
        coordinator.async_refresh.assert_awaited_once_with()

    async def test_native_todo_deletion_without_response_keyword(self):
        self.response.json.return_value = None
        coordinator = SimpleNamespace(api=self.client, async_refresh=AsyncMock())
        entity = self.todo_class(coordinator, "entry-1", "project-1", "Test project")
        await entity.async_delete_todo_items(["task-1"])
        self.assert_http_call("delete")
        coordinator.async_refresh.assert_awaited_once_with()

    async def test_get_and_create_service_response_modes_remain_raw(self):
        for operation in ("get", "create"):
            with self.subTest(operation=operation):
                self.setUp()
                self.response.json.return_value = self.task_data
                handler = await getattr(self.handlers, f"handle_{operation}_task")(self.client)
                data = self.ids if operation == "get" else {
                    "projectId": "project-1", "title": "Regression task"
                }
                result = await handler(SimpleNamespace(data=data))
                self.assertEqual(result, {"data": self.task_data})
                self.assertIs(result["data"], self.task_data)
                method = self.session.get if operation == "get" else self.session.post
                self.assertEqual(method.await_count, 1)
                if operation == "create":
                    self.assertEqual(json.loads(method.call_args.kwargs["data"]), data)

    async def test_get_and_create_direct_calls_still_convert_models(self):
        for operation in ("get", "create"):
            for options in ({}, {"returnAsJson": False}, {"returnAsJson": True}):
                with self.subTest(operation=operation, options=options):
                    self.setUp()
                    self.response.json.return_value = self.task_data
                    args = self.ids if operation == "get" else {
                        "task": self.Task(projectId="project-1", title="Regression task")
                    }
                    result = await getattr(self.client, f"{operation}_task")(**args, **options)
                    if options.get("returnAsJson"):
                        self.assertIs(result, self.task_data)
                    else:
                        self.assertIsInstance(result, self.Task)
                        self.assertEqual(result.id, "task-1")
                        self.assertEqual(result.title, "Regression task")

    async def test_complete_and_delete_http_errors_still_surface_in_service_response(self):
        for operation in ("complete", "delete"):
            with self.subTest(operation=operation):
                self.setUp()
                self.response.ok = False
                self.response.status = 403
                self.response.json.return_value = {"error": "forbidden"}
                handler = await getattr(self.handlers, f"handle_{operation}_task")(self.client)
                result = await handler(SimpleNamespace(data=self.ids))
                self.assertIn("status code: 403", result["error"])
                self.assertNotIn("data", result)
                self.assert_http_call(operation)


if __name__ == "__main__":
    unittest.main()

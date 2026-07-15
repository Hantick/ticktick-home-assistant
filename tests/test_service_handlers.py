import importlib.util
import sys
import types
import unittest
from pathlib import Path
from types import SimpleNamespace


def _install_homeassistant_stubs() -> None:
    homeassistant = types.ModuleType("homeassistant")
    core_mod = types.ModuleType("homeassistant.core")
    components_mod = types.ModuleType("homeassistant.components")
    http_mod = types.ModuleType("homeassistant.components.http")
    config_entries_mod = types.ModuleType("homeassistant.config_entries")
    const_mod = types.ModuleType("homeassistant.const")
    helpers_mod = types.ModuleType("homeassistant.helpers")
    aiohttp_client_mod = types.ModuleType("homeassistant.helpers.aiohttp_client")

    class ServiceCall:
        def __init__(self, data):
            self.data = data

    class ConfigEntry:
        pass

    class HomeAssistant:
        pass

    class SupportsResponse:
        ONLY = "only"
        OPTIONAL = "optional"

    async def async_import_module(*args, **kwargs):
        return None

    core_mod.ServiceCall = ServiceCall
    core_mod.HomeAssistant = HomeAssistant
    core_mod.SupportsResponse = SupportsResponse
    homeassistant.core = core_mod

    http_mod.async_import_module = async_import_module
    components_mod.http = http_mod
    config_entries_mod.ConfigEntry = ConfigEntry
    const_mod.Platform = object
    helpers_mod.aiohttp_client = aiohttp_client_mod
    aiohttp_client_mod.async_get_clientsession = lambda *args, **kwargs: None

    util_mod = types.ModuleType("homeassistant.util")
    dt_mod = types.ModuleType("homeassistant.util.dt")
    dt_mod.get_default_time_zone = lambda: None
    util_mod.dt = dt_mod
    homeassistant.util = util_mod

    aiohttp_mod = types.ModuleType("aiohttp")

    class ClientSession:
        pass

    class ClientResponse:
        pass

    aiohttp_mod.ClientSession = ClientSession
    aiohttp_mod.ClientResponse = ClientResponse

    sys.modules.setdefault("aiohttp", aiohttp_mod)
    sys.modules.setdefault("homeassistant", homeassistant)
    sys.modules.setdefault("homeassistant.core", core_mod)
    sys.modules.setdefault("homeassistant.components", components_mod)
    sys.modules.setdefault("homeassistant.components.http", http_mod)
    sys.modules.setdefault("homeassistant.config_entries", config_entries_mod)
    sys.modules.setdefault("homeassistant.const", const_mod)
    sys.modules.setdefault("homeassistant.helpers", helpers_mod)
    sys.modules.setdefault("homeassistant.helpers.aiohttp_client", aiohttp_client_mod)
    sys.modules.setdefault("homeassistant.util", util_mod)
    sys.modules.setdefault("homeassistant.util.dt", dt_mod)


_install_homeassistant_stubs()

package_root = Path(__file__).resolve().parents[1] / "custom_components"
package_name = "custom_components.ticktick"
package_module = types.ModuleType(package_name)
package_module.__path__ = [str(package_root / "ticktick")]
sys.modules[package_name] = package_module

module_path = package_root / "ticktick" / "service_handlers.py"
spec = importlib.util.spec_from_file_location(package_name + ".service_handlers", module_path)
service_handlers = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = service_handlers
spec.loader.exec_module(service_handlers)


class DummyClient:
    def __init__(self) -> None:
        self.calls = []

    async def get_uid_from_task_summary(self, summary: str, returnAsJson: bool = False):
        self.calls.append((summary, returnAsJson))
        return "uid-123"


class ServiceHandlersTests(unittest.TestCase):
    def test_handle_get_uid_from_task_summary_uses_summary_argument(self) -> None:
        client = DummyClient()

        async def run_test() -> None:
            handler = await service_handlers.handle_get_uid_from_task_summary(client)
            result = await handler(SimpleNamespace(data={"summary": "Test task"}))
            self.assertEqual(result, {"data": "uid-123"})
            self.assertEqual(client.calls, [("Test task", True)])

        import asyncio

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()

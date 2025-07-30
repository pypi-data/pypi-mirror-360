from pathlib import Path
from typing import Callable

from decouple import config
from sanic import Sanic

from salute.common.utils.load_data import load_data
from salute.common.models.request_message import RequestMessage
from salute.common.models.response_message import ResponseMessage
from salute.common.models.scenario.utils import ScenarioInfo
from salute.common.store.store import StoreProvider


class SessionStore:
    get: Callable
    set: Callable
    drop: Callable

    def __init__(self, get, set, drop) -> None:
        self.get = get
        self.set = set
        self.drop = drop


class ScenarioApp:
    def __init__(self, path: Path, *args, **kwargs) -> None:
        self.static_dir = Path(path) / "static"
        self.info: ScenarioInfo = self._set_scenario_config()
        self.storage: StoreProvider = Sanic.get_app(config("NAME")).config["STORAGE"]
        self.session_store: SessionStore = SessionStore(
            self.get_session,
            self.set_session,
            self.drop_session,
        )

    def _set_scenario_config(self) -> ScenarioInfo:
        data = load_data(self.static_dir / "intent.json")
        return ScenarioInfo(**data)

    async def set_storage(self) -> None:
        await self.storage.init(self.info.key)

    async def get_session(self, key: str) -> dict:
        return await self.storage.get(key, self.info.key)

    async def set_session(self, key: str, data: dict) -> bool:
        return await self.storage.save_or_update(key, data, self.info.key)

    async def drop_session(self, key: str) -> bool:
        return await self.storage.remove(key, self.info.key)

    async def process(self, scenario_request: RequestMessage) -> ResponseMessage:
        pass

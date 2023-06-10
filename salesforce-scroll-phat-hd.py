import settings
import scrollphathd
from scrollphathd.fonts import font5x7
import misaki

import asyncio
from aiosfstream.auth import AuthenticatorBase
from aiosfstream.replay import ReplayOption, ReplayMarkerStorage, ReplayMarker
from aiocometd.typing import JsonObject, JsonLoader, JsonDumper
from aiosfstream.client import Client, ReplayMarkerStoragePolicy
from aiohttp import ClientSession

from typing import Optional, Union, MutableMapping, Type, Tuple
import json
import threading
import time

class ClientCredentialAuthenticator(AuthenticatorBase):
    def __init__(self, consumer_key: str, consumer_secret: str,
                 sandbox: bool = False,
                 json_dumps: JsonDumper = json.dumps,
                 json_loads: JsonLoader = json.loads) -> None:
        super().__init__(sandbox=sandbox,
                         json_dumps=json_dumps,
                         json_loads=json_loads)
        self.client_id = consumer_key
        self.client_secret = consumer_secret

    @property
    def _token_url(self) -> str:
        if self._sandbox:
            return settings.token_url
        return settings.token_url

    def __repr__(self) -> str:
        cls_name = type(self).__name__
        return f"{cls_name}(consumer_key={reprlib.repr(self.client_id)}," \
               f"consumer_secret={reprlib.repr(self.client_secret)})"

    async def _authenticate(self) -> Tuple[int, JsonObject]:
        async with ClientSession(json_serialize=self.json_dumps) as session:
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            response = await session.post(self._token_url, data=data)
            response_data = await response.json(loads=self.json_loads)
            return response.status, response_data

ReplayParameter = Union[ReplayOption,
                        ReplayMarkerStorage,
                        MutableMapping[str, ReplayMarker]]

class SalesforceStreamingClientWithClientCredential(Client):
    def __init__(self, *,  # pylint: disable=too-many-locals
                 consumer_key: str, consumer_secret: str,
                 replay: ReplayParameter = ReplayOption.NEW_EVENTS,
                 replay_fallback: Optional[ReplayOption] = None,
                 replay_storage_policy: ReplayMarkerStoragePolicy
                 = ReplayMarkerStoragePolicy.AUTOMATIC,
                 connection_timeout: Union[int, float] = 10.0,
                 max_pending_count: int = 100, sandbox: bool = False,
                 json_dumps: JsonDumper = json.dumps,
                 json_loads: JsonLoader = json.loads,
                 loop: Optional[asyncio.AbstractEventLoop] = None):
        authenticator = ClientCredentialAuthenticator(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            sandbox=sandbox,
            json_dumps=json_dumps,
            json_loads=json_loads,
        )
        super().__init__(
            authenticator,
            replay=replay,
            replay_fallback=replay_fallback,
            replay_storage_policy=replay_storage_policy,
            connection_timeout=connection_timeout,
            max_pending_count=max_pending_count,
            json_dumps=json_dumps,
            json_loads=json_loads,
            loop=loop
        )

async def subscribeToSalesforce():
    async with SalesforceStreamingClientWithClientCredential(
            consumer_key= settings.consumer_key,
            consumer_secret = settings.consumer_secret) as client:

        await client.subscribe(settings.platform_event_channel)
        async for message in client:
            topic = message["channel"]
            data = message["data"]
            print(f"{topic}: {data}")
            pe = json.loads(json.dumps(data))
            scrollphathd.clear()
            scrollphathd.write_string(pe["payload"][settings.message_field], font=misaki, brightness=settings.brightness)

def message_thread():
    while True:
        scrollphathd.show()
        scrollphathd.scroll()
        time.sleep(0.1)

if __name__ == "__main__":
    thread = threading.Thread(target = message_thread, name = "message", args = ())
    thread.start()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(subscribeToSalesforce())


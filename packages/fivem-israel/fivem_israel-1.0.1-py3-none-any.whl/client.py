import asyncio
import websockets
import json

class FiveMIsrael:
    def __init__(self, api_key):
        self.url = f"wss://votes.fivemisrael.com?token={api_key}"
        self._events = {}

    def event(self, coro):
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("Registered event must be a coroutine function")
        self._events[coro.__name__] = coro
        return coro

    async def _dispatch(self, event_name, *args, **kwargs):
        if event_name in self._events:
            await self._events[event_name](*args, **kwargs)

    async def start(self):
        await self._dispatch("on_ready")
        while True:
            try:
                async with websockets.connect(self.url, ping_interval=20, ping_timeout=10) as ws:
                    await self._dispatch("on_connect")
                    async for message in ws:
                        data = json.loads(message)
                        if data.get("type") == "vote":
                            await self._dispatch("on_vote", data["data"])
            except Exception as e:
                await self._dispatch("on_error", e)
                await asyncio.sleep(5)

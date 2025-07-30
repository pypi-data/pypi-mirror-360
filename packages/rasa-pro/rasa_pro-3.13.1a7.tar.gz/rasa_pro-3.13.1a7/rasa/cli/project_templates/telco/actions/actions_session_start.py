import asyncio

from rasa_sdk import Action
from rasa_sdk.events import EventType


class ActionSleepAndRespond(Action):
    def name(self) -> str:
        return "action_sleep_few_sec"

    async def run(self, dispatcher, tracker, domain) -> list[EventType]:
        await asyncio.sleep(3)
        return []

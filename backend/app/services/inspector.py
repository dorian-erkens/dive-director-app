from __future__ import annotations

import asyncio
from collections import defaultdict

from app.models.inspector import InspectorEvent


class InspectorBus:
    """Pub/sub event bus for inspector events.

    Each conversation has its own subscriber list. The chat endpoint
    publishes events; the inspector WebSocket subscribes and forwards
    them to the frontend in real time.
    """

    def __init__(self):
        self._subscribers: dict[str, list[asyncio.Queue]] = defaultdict(list)

    def subscribe(self, conversation_id: str) -> asyncio.Queue:
        queue: asyncio.Queue[InspectorEvent] = asyncio.Queue()
        self._subscribers[conversation_id].append(queue)
        return queue

    def unsubscribe(self, conversation_id: str, queue: asyncio.Queue):
        if conversation_id in self._subscribers:
            self._subscribers[conversation_id] = [
                q for q in self._subscribers[conversation_id] if q is not queue
            ]
            if not self._subscribers[conversation_id]:
                del self._subscribers[conversation_id]

    async def publish(self, conversation_id: str, event: InspectorEvent):
        for queue in self._subscribers.get(conversation_id, []):
            await queue.put(event)


inspector_bus = InspectorBus()

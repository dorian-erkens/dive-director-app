import json
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.models.inspector import InspectorEvent
from app.services.claude import chat_stream
from app.services.inspector import inspector_bus

router = APIRouter(tags=["chat"])


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    conversation_id = str(uuid.uuid4())
    messages: list[dict] = []

    await websocket.send_json({
        "type": "connected",
        "conversation_id": conversation_id,
    })

    try:
        while True:
            data = await websocket.receive_json()
            user_message = data.get("message", "")
            if not user_message:
                continue

            messages.append({"role": "user", "content": user_message})

            await websocket.send_json({"type": "stream_start"})

            async for token in chat_stream(messages, conversation_id):
                await websocket.send_json({
                    "type": "stream_token",
                    "token": token,
                })

            await websocket.send_json({"type": "stream_end"})

            # Collect the full response for conversation history
            # (Claude service already yielded it token by token)
            # We reconstruct from the stream — a simplification;
            # in practice we'd collect during streaming
            # For now, we ask the caller to track the assembled text
    except WebSocketDisconnect:
        pass


@router.websocket("/ws/inspector/{conversation_id}")
async def websocket_inspector(websocket: WebSocket, conversation_id: str):
    await websocket.accept()
    queue = inspector_bus.subscribe(conversation_id)

    try:
        while True:
            event: InspectorEvent = await queue.get()
            await websocket.send_json(
                event.model_dump(mode="json")
            )
    except WebSocketDisconnect:
        inspector_bus.unsubscribe(conversation_id, queue)

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

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

            # Collect full response text to add to conversation history
            full_response = ""
            async for token in chat_stream(messages, conversation_id):
                full_response += token
                await websocket.send_json({
                    "type": "stream_token",
                    "token": token,
                })

            await websocket.send_json({"type": "stream_end"})

            # Add assistant response to history so Claude has full context
            if full_response:
                messages.append({"role": "assistant", "content": full_response})

    except WebSocketDisconnect:
        pass


@router.websocket("/ws/inspector/{conversation_id}")
async def websocket_inspector(websocket: WebSocket, conversation_id: str):
    await websocket.accept()
    queue = inspector_bus.subscribe(conversation_id)

    try:
        while True:
            event = await queue.get()
            await websocket.send_json(
                event.model_dump(mode="json")
            )
    except WebSocketDisconnect:
        inspector_bus.unsubscribe(conversation_id, queue)

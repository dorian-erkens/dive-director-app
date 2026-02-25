from __future__ import annotations

import json
import os
from typing import AsyncGenerator

import anthropic

from app.models.inspector import AgentName, EventType, InspectorEvent
from app.services import shom
from app.services.inspector import inspector_bus

SYSTEM_PROMPT = """Tu es l'assistant du Directeur de Plongée (DP) du club Caen Ouistreham Plongée (COP).
Tu opères depuis le port d'Ouistreham (49°17'N, 000°15'W) à bord du CIPI'ONE.

Tu aides à planifier, organiser et sécuriser les sorties plongée en Baie de Seine.

Tu as accès aux outils suivants :
- search_wreck_by_name : chercher une épave par nom dans la base SHOM (4796+ épaves)
- get_nearby_wrecks : trouver les épaves autour d'un point GPS
- search_wrecks_bbox : chercher les épaves dans une zone rectangulaire
- get_wreck_details : obtenir les détails complets d'une épave par son ID SHOM

Conventions :
- Profondeurs en mètres (préciser sonde vs profondeur réelle)
- Distances en milles nautiques (NM)
- Positions GPS en degrés-minutes décimales ET degrés décimaux
- Caps en degrés vrais (000°-360°)
- Réponds en français par défaut

Sécurité : ne jamais minimiser un risque. La décision finale appartient toujours au DP.
CROSS 196, VHF canal 16.
"""

TOOLS = [
    {
        "name": "search_wreck_by_name",
        "description": "Chercher une épave par nom (partiel, insensible à la casse) dans la base SHOM.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Nom de l'épave à chercher",
                }
            },
            "required": ["name"],
        },
    },
    {
        "name": "get_nearby_wrecks",
        "description": "Trouver les épaves autour d'un point GPS, triées par distance.",
        "input_schema": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number", "description": "Latitude du point de référence"},
                "longitude": {"type": "number", "description": "Longitude du point de référence"},
                "radius_nm": {
                    "type": "number",
                    "description": "Rayon de recherche en milles nautiques",
                },
            },
            "required": ["latitude", "longitude", "radius_nm"],
        },
    },
    {
        "name": "search_wrecks_bbox",
        "description": "Chercher les épaves dans une zone rectangulaire (bounding box).",
        "input_schema": {
            "type": "object",
            "properties": {
                "min_lat": {"type": "number", "description": "Latitude sud"},
                "max_lat": {"type": "number", "description": "Latitude nord"},
                "min_lon": {"type": "number", "description": "Longitude ouest"},
                "max_lon": {"type": "number", "description": "Longitude est"},
            },
            "required": ["min_lat", "max_lat", "min_lon", "max_lon"],
        },
    },
    {
        "name": "get_wreck_details",
        "description": "Obtenir la fiche complète d'une épave par son ID SHOM.",
        "input_schema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "ID SHOM (ex: 'wrecks.42' ou '42')"}
            },
            "required": ["id"],
        },
    },
]


async def _execute_tool(tool_name: str, tool_input: dict, conversation_id: str) -> str:
    await inspector_bus.publish(
        conversation_id,
        InspectorEvent(
            type=EventType.TOOL_CALL,
            agent=AgentName.WRECK_FINDER,
            title=f"Appel outil: {tool_name}",
            content=json.dumps(tool_input, ensure_ascii=False, indent=2),
            metadata={"tool": tool_name, "input": tool_input},
        ),
    )

    try:
        if tool_name == "search_wreck_by_name":
            wrecks = await shom.search_by_name(tool_input["name"])
            result = [w.model_dump() for w in wrecks]
        elif tool_name == "get_nearby_wrecks":
            wrecks = await shom.get_nearby(
                tool_input["latitude"],
                tool_input["longitude"],
                tool_input["radius_nm"],
            )
            result = [w.model_dump() for w in wrecks]
        elif tool_name == "search_wrecks_bbox":
            wrecks = await shom.search_bbox(
                tool_input["min_lat"],
                tool_input["max_lat"],
                tool_input["min_lon"],
                tool_input["max_lon"],
            )
            result = [w.model_dump() for w in wrecks]
        elif tool_name == "get_wreck_details":
            wreck = await shom.get_details(tool_input["id"])
            result = wreck.model_dump() if wreck else {"error": "Épave non trouvée"}
        else:
            result = {"error": f"Outil inconnu: {tool_name}"}

        result_str = json.dumps(result, ensure_ascii=False, default=str)

        await inspector_bus.publish(
            conversation_id,
            InspectorEvent(
                type=EventType.TOOL_RESULT,
                agent=AgentName.WRECK_FINDER,
                title=f"Résultat: {tool_name}",
                content=f"{len(result) if isinstance(result, list) else 1} résultat(s)",
                metadata={"tool": tool_name, "count": len(result) if isinstance(result, list) else 1},
            ),
        )

        return result_str

    except Exception as e:
        error_msg = f"Erreur lors de l'appel à {tool_name}: {e}"
        await inspector_bus.publish(
            conversation_id,
            InspectorEvent(
                type=EventType.ERROR,
                agent=AgentName.WRECK_FINDER,
                title=f"Erreur: {tool_name}",
                content=str(e),
            ),
        )
        return json.dumps({"error": error_msg})


async def chat_stream(
    messages: list[dict],
    conversation_id: str,
) -> AsyncGenerator[str, None]:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        yield "Erreur: ANTHROPIC_API_KEY non configurée."
        return

    client = anthropic.AsyncAnthropic(api_key=api_key)

    await inspector_bus.publish(
        conversation_id,
        InspectorEvent(
            type=EventType.AGENT_CALL,
            agent=AgentName.ORCHESTRATOR,
            title="Envoi à Claude",
            content=f"{len(messages)} message(s) dans la conversation",
            metadata={"message_count": len(messages)},
        ),
    )

    current_messages = list(messages)

    while True:
        collected_text = ""
        tool_uses = []
        stop_reason = None

        async with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=current_messages,
            tools=TOOLS,
        ) as stream:
            async for event in stream:
                if event.type == "content_block_start":
                    if event.content_block.type == "tool_use":
                        tool_uses.append({
                            "id": event.content_block.id,
                            "name": event.content_block.name,
                            "input_json": "",
                        })
                elif event.type == "content_block_delta":
                    if event.delta.type == "text_delta":
                        collected_text += event.delta.text
                        yield event.delta.text
                    elif event.delta.type == "input_json_delta":
                        if tool_uses:
                            tool_uses[-1]["input_json"] += event.delta.partial_json

            final_message = await stream.get_final_message()
            stop_reason = final_message.stop_reason

        if stop_reason != "tool_use" or not tool_uses:
            break

        assistant_content = []
        if collected_text:
            assistant_content.append({"type": "text", "text": collected_text})
        for tu in tool_uses:
            assistant_content.append({
                "type": "tool_use",
                "id": tu["id"],
                "name": tu["name"],
                "input": json.loads(tu["input_json"]) if tu["input_json"] else {},
            })

        current_messages.append({"role": "assistant", "content": assistant_content})

        tool_results = []
        for tu in tool_uses:
            tool_input = json.loads(tu["input_json"]) if tu["input_json"] else {}
            result = await _execute_tool(tu["name"], tool_input, conversation_id)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tu["id"],
                "content": result,
            })

        current_messages.append({"role": "user", "content": tool_results})
        collected_text = ""
        tool_uses = []

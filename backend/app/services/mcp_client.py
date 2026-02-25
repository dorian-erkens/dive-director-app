"""MCP client for mcp-shom-wrecks server.

Replaces the old shom.py direct HTTP client. All SHOM data now flows
through the single mcp-shom-wrecks server via JSON-RPC 2.0 over stdio.

Architecture:
    FastAPI backend  --[JSON-RPC/stdio]-->  mcp-shom-wrecks  --[HTTPS/WFS]-->  SHOM API
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from app.models.wrecks import NearbyWreck, Wreck


class McpShomClient:
    """Async MCP client that manages the mcp-shom-wrecks subprocess."""

    def __init__(self, mcp_path: str | None = None):
        self._mcp_path = mcp_path or os.environ.get(
            "MCP_SHOM_PATH",
            os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "..", "..", "..", "..",
                    "mcp-shom-wrecks", "dist", "index.js",
                )
            ),
        )
        self._process: asyncio.subprocess.Process | None = None
        self._request_id = 0
        self._lock = asyncio.Lock()
        self._initialized = False

    async def _ensure_started(self):
        """Start the MCP server subprocess if not already running."""
        if self._process is not None and self._process.returncode is None:
            return

        if not os.path.exists(self._mcp_path):
            raise FileNotFoundError(
                f"MCP server not found at {self._mcp_path}. "
                "Run 'npm run build' in mcp-shom-wrecks/ first."
            )

        self._process = await asyncio.create_subprocess_exec(
            "node", self._mcp_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        self._initialized = False

    async def _send(self, message: dict) -> dict | None:
        """Send a JSON-RPC message. Returns response for requests, None for notifications."""
        assert self._process and self._process.stdin and self._process.stdout

        data = json.dumps(message) + "\n"
        self._process.stdin.write(data.encode())
        await self._process.stdin.drain()

        if "id" not in message:
            return None

        while True:
            line = await asyncio.wait_for(
                self._process.stdout.readline(),
                timeout=30,
            )
            if not line:
                raise ConnectionError("MCP server closed unexpectedly")
            try:
                response = json.loads(line.decode())
                if response.get("id") == message["id"]:
                    return response
            except json.JSONDecodeError:
                continue

    async def _initialize(self):
        """Send MCP initialize handshake."""
        if self._initialized:
            return

        self._request_id += 1
        await self._send({
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "dive-director-backend", "version": "0.1.0"},
            },
        })

        await self._send({
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        })

        self._initialized = True

    # ── Low-level: raw MCP tool call ─────────────────────────────────

    async def call_tool(self, tool_name: str, arguments: dict) -> str:
        """Call an MCP tool and return the raw text content.

        Used by claude.py to pass tool results directly to Claude.
        """
        async with self._lock:
            await self._ensure_started()
            await self._initialize()

            self._request_id += 1
            response = await self._send({
                "jsonrpc": "2.0",
                "id": self._request_id,
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": arguments},
            })

        if not response:
            raise RuntimeError("No response from MCP server")
        if "error" in response:
            raise RuntimeError(f"MCP error: {response['error']}")

        content = response.get("result", {}).get("content", [])
        if content and content[0].get("type") == "text":
            return content[0]["text"]

        return "{}"

    async def call_tool_parsed(self, tool_name: str, arguments: dict) -> Any:
        """Call an MCP tool and return parsed JSON.

        Used by REST endpoints that need structured Pydantic models.
        """
        text = await self.call_tool(tool_name, arguments)
        return json.loads(text)

    # ── High-level: typed methods for REST API ───────────────────────

    async def search_by_name(self, name: str) -> list[Wreck]:
        result = await self.call_tool_parsed("search_wreck_by_name", {"name": name})
        return [_to_wreck(w) for w in result.get("wrecks", [])]

    async def get_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_nm: float,
        max_results: int = 50,
    ) -> list[NearbyWreck]:
        args: dict[str, Any] = {
            "latitude": latitude,
            "longitude": longitude,
            "radius_nm": radius_nm,
        }
        if max_results:
            args["max_results"] = max_results
        result = await self.call_tool_parsed("get_nearby_wrecks", args)
        return [_to_nearby_wreck(w) for w in result.get("wrecks", [])]

    async def search_bbox(
        self,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        max_results: int = 200,
    ) -> list[Wreck]:
        args: dict[str, Any] = {
            "min_lat": min_lat,
            "max_lat": max_lat,
            "min_lon": min_lon,
            "max_lon": max_lon,
        }
        if max_results:
            args["max_results"] = max_results
        result = await self.call_tool_parsed("search_wrecks_bbox", args)
        return [_to_wreck(w) for w in result.get("wrecks", [])]

    async def get_details(self, wreck_id: str) -> Wreck | None:
        result = await self.call_tool_parsed("get_wreck_details", {"id": wreck_id})
        if result.get("error"):
            return None
        return _to_wreck(result)

    async def close(self):
        if self._process and self._process.returncode is None:
            self._process.terminate()
            await self._process.wait()


# ── Field mapping: SHOM French names → English model names ───────────

def _to_wreck(data: dict) -> Wreck:
    return Wreck(
        id=data.get("id", ""),
        name=data.get("nom"),
        latitude=data.get("latitude", 0),
        longitude=data.get("longitude", 0),
        depth=data.get("brassiage"),
        depth_precision=data.get("precis_bra"),
        ship_info=data.get("caract_bat"),
        object_condition=data.get("caract_obj"),
        sinking_circumstances=data.get("circ_nauf"),
        object_length=data.get("long_obj"),
        position_precision=data.get("precis_loc"),
        object_type=data.get("type_obj"),
        inspire_id=data.get("inspireid"),
    )


def _to_nearby_wreck(data: dict) -> NearbyWreck:
    return NearbyWreck(
        **_to_wreck(data).model_dump(),
        distance_nm=data.get("distance_nm", 0),
        bearing=data.get("bearing_deg", 0),
    )


# ── Singleton ────────────────────────────────────────────────────────

_client: McpShomClient | None = None


async def get_client() -> McpShomClient:
    global _client
    if _client is None:
        _client = McpShomClient()
    return _client

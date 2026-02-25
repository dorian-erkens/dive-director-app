from __future__ import annotations

from pydantic import BaseModel
from enum import Enum
from datetime import datetime


class EventType(str, Enum):
    AGENT_CALL = "agent_call"
    AGENT_RESULT = "agent_result"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    DECISION = "decision"
    WARNING = "warning"
    ERROR = "error"
    THINKING = "thinking"


class AgentName(str, Enum):
    WRECK_FINDER = "wreck-finder"
    TIDE_CALCULATOR = "tide-calculator"
    DIVE_CONDITIONS = "dive-conditions"
    FFESSM_EXPERT = "ffessm-expert"
    SAFETY_SHEET = "safety-sheet"
    BOAT_SPECS = "boat-specs"
    NAV_CALCULATOR = "nav-calculator"
    ORCHESTRATOR = "orchestrator"


class InspectorEvent(BaseModel):
    type: EventType
    agent: AgentName | None = None
    title: str
    content: str
    metadata: dict | None = None
    timestamp: datetime | None = None

    def model_post_init(self, __context):
        if self.timestamp is None:
            self.timestamp = datetime.now()

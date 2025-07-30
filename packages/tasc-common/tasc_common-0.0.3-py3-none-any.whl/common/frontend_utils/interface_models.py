from typing import List, Dict, Any, Literal, TYPE_CHECKING
from enum import Enum
from pydantic import BaseModel, Field
from actx.interface_models import Attachment, MessageRead
from common.intel.bot import ToolCall


class EventType(str, Enum):
    CHAT = "chat"
    SESSION_UPDATE = "session_update"
    ERROR = "error"
    SESSION_WAKE = "session_wake"
    SESSION_SLEEP = "session_sleep"
    BOT_AGENT_LOOP_START = "session_bot_agent_loop_start"
    BOT_AGENT_LOOP_END = "session_bot_agent_loop_iteration_end"
    BOT_THINKING = "session_bot_thinking"
    BOT_TOOL_CALL = "session_bot_tool_call"
    BOT_TOOL_RESPONSE = "session_bot_tool_response"
    SESSION_TITLE_UPDATE = "agent_session_title_update"
    DOSSIER_UPDATE = "dossier_update"
    SESSION_AUTO_RECALL = "session_auto_recall"

class Participant(BaseModel):
    phone: str | None = None
    email: str | None = None
    name: str
    role: str


# Base model for all SSE messages
class SSEMessageBase(BaseModel):
    event_type: EventType

# Chat message with content and attachments
class ChatMessage(SSEMessageBase):
    event_type: Literal[EventType.CHAT] = EventType.CHAT
    sender: str
    content: str | None = None
    timestamp: str
    attachments: List[Attachment] = []
    message_id: str | None = None  # Added to track message for updates

    @classmethod
    def from_message_read(cls, message: MessageRead) -> "ChatMessage":
        """Convert a MessageRead object to a ChatMessage."""
        return cls(
            type="chat",
            sender=message.payload.sender,
            content=message.payload.content,
            timestamp=str(message.created_at),
            attachments=message.payload.attachments,
            message_id=message.id,
        )


# Session metadata updates
class SessionUpdateMessage(SSEMessageBase):
    event_type: Literal[EventType.SESSION_UPDATE] = EventType.SESSION_UPDATE
    session_id: str
    title: str | None = None
    metadata: dict | None = None


# Error messages
class ErrorMessage(SSEMessageBase):
    event_type: Literal[EventType.ERROR] = EventType.ERROR
    code: str
    message: str
    details: dict | None = None


class SessionWakeEvent(SSEMessageBase):
    event_type: Literal[EventType.SESSION_WAKE] = EventType.SESSION_WAKE
    agent_session_id: str
    wake_context: Dict[str, Any]


class SessionAgentLoopIterationStartEvent(SSEMessageBase):
    event_type: Literal[EventType.BOT_AGENT_LOOP_START] = EventType.BOT_AGENT_LOOP_START
    agent_session_id: str
    cycle: int
    step: int


class SessionAgentLoopIterationEndEvent(SSEMessageBase):
    event_type: Literal[EventType.BOT_AGENT_LOOP_END] = EventType.BOT_AGENT_LOOP_END
    agent_session_id: str
    cycle: int
    step: int


class SessionSleepEvent(SSEMessageBase):
    event_type: Literal[EventType.SESSION_SLEEP] = EventType.SESSION_SLEEP
    agent_session_id: str
    cycle: int
    step: int


class SessionBotThinkingEvent(SSEMessageBase):
    event_type: Literal[EventType.BOT_THINKING] = EventType.BOT_THINKING
    agent_session_id: str
    thoughts: str


class SessionBotToolCallEvent(SSEMessageBase):
    event_type: Literal[EventType.BOT_TOOL_CALL] = EventType.BOT_TOOL_CALL
    agent_session_id: str
    tool_calls: List[ToolCall]


class SessionBotToolResponseEvent(SSEMessageBase):
    event_type: Literal[EventType.BOT_TOOL_RESPONSE] = EventType.BOT_TOOL_RESPONSE
    agent_session_id: str
    tool_response: Dict[str, Any] | None


class AgentSessionTitleUpdateEvent(SSEMessageBase):
    event_type: Literal[EventType.SESSION_TITLE_UPDATE] = EventType.SESSION_TITLE_UPDATE
    agent_session_id: str
    session_title: str

class DossierUpdateEvent(SSEMessageBase):
    event_type: Literal[EventType.DOSSIER_UPDATE] = EventType.DOSSIER_UPDATE
    dossier: str
    usecases: List[Dict[str, Any]]

class SessionAutoRecallEvent(SSEMessageBase):
    event_type: Literal[EventType.SESSION_AUTO_RECALL] = EventType.SESSION_AUTO_RECALL
    agent_session_id: str
    memory_summary: str

# Discriminated union of all possible message types
SSEMessage = (
    ChatMessage | 
    SessionUpdateMessage | 
    ErrorMessage | 
    SessionWakeEvent | 
    SessionSleepEvent |
    SessionAgentLoopIterationStartEvent |
    SessionAgentLoopIterationEndEvent |
    SessionBotThinkingEvent |
    SessionBotToolCallEvent |
    SessionBotToolResponseEvent |
    AgentSessionTitleUpdateEvent |
    DossierUpdateEvent |
    SessionAutoRecallEvent
)

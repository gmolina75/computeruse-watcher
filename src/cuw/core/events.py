from __future__ import annotations
from pathlib import Path
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def utc_iso(dt: datetime | None = None) -> str:
    return (dt or utc_now()).isoformat()

class EventId:
    """Simple UUIDv4 event id generation."""
    @staticmethod
    def new() -> str:
        return str(uuid.uuid4())

class EventBase(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)
    event_id: str = Field(default_factory=EventId.new)
    hostname: str
    os: str
    os_version: str
    username: str | None = None
    timestamp: str = Field(default_factory=utc_iso)

class SystemEvent(EventBase):
    event_type: str = "system"
    status: str

class SessionEvent(EventBase):
    event_type: str = "session"
    action: str  # login/logout

class FocusEvent(EventBase):
    event_type: str = "focus_change"
    process_name: str = ""
    window_title: str = ""
    start_time: str
    duration_seconds: float | None = None

class IdleEvent(EventBase):
    event_type: str = "idle"
    idle_seconds: float

def make_payload(event: EventBase) -> dict:
    return event.model_dump(mode="json")

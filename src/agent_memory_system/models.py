from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class MemoryLayer(str, Enum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"


class MemoryScope(str, Enum):
    SESSION = "session"
    USER = "user"
    AGENT = "agent"


class MemoryRecord(BaseModel):
    id: Optional[str] = None
    layer: MemoryLayer = MemoryLayer.WORKING
    scope: MemoryScope = MemoryScope.SESSION
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    decay: float = Field(default=0.05, ge=0.0, le=1.0)
    embedding: Optional[list[float]] = None
    content: str = ""
    record_metadata: dict = Field(default_factory=dict, alias="metadata")

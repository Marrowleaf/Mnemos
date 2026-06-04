from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MemoryLayer(str, Enum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"

class MemoryScope(str, Enum):
    SESSION = "session"
    USER = "user"
    AGENT = "agent"


class MemoryTier(str, Enum):
    FACT = "fact"
    EVENT = "event"
    PREFERENCE = "preference"
    GOAL = "goal"
    RELATIONSHIP = "relationship"
    KNOWLEDGE = "knowledge"


class HierarchyPath(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    tier: MemoryTier = MemoryTier.FACT
    parent_id: Optional[str] = Field(default=None, alias="parentId")
    path: str = "/"


class MemoryPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    path: HierarchyPath = Field(default_factory=HierarchyPath)
    summary: str = ""
    detail: Optional[str] = Field(default=None, alias="detail")
    context: Optional[dict[str, Any]] = Field(default=None, alias="context")


class MemoryRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = Field(default=None, alias="id")
    layer: MemoryLayer = Field(MemoryLayer.WORKING, alias="layer")
    tier: MemoryTier = Field(MemoryTier.FACT, alias="tier")
    path: HierarchyPath = Field(default_factory=HierarchyPath, alias="path")
    scope: MemoryScope = Field(MemoryScope.SESSION, alias="scope")
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias="updatedAt")
    expires_at: Optional[datetime] = Field(default=None, alias="expiresAt")
    importance: float = Field(default=0.5, alias="importance")
    decay: float = Field(default=0.0, alias="decay")
    embedding: Optional[list[float]] = Field(default=None, alias="embedding")
    payload: MemoryPayload = Field(default_factory=MemoryPayload, alias="payload")
    content: str = Field(default="", alias="content")
    metadata: Optional[dict[str, Any]] = Field(default=None, alias="metadata")

    def to_public(self) -> dict[str, Any]:
        data = self.model_dump(by_alias=True)
        data.setdefault("id", self.id)
        data.setdefault("metadata", self.metadata)
        return data

    @field_validator("layer", mode="before")
    @classmethod
    def coerce_layer(cls, value: Any) -> MemoryLayer:
        if isinstance(value, MemoryLayer):
            return value
        return MemoryLayer(value)

    @field_validator("tier", mode="before")
    @classmethod
    def coerce_tier(cls, value: Any) -> MemoryTier:
        if isinstance(value, MemoryTier):
            return value
        return MemoryTier(value)

    @field_validator("scope", mode="before")
    @classmethod
    def coerce_scope(cls, value: Any) -> MemoryScope:
        if isinstance(value, MemoryScope):
            return value
        return MemoryScope(value)

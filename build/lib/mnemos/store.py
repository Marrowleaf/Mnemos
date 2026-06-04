from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String
from sqlalchemy.orm import declarative_base

from mnemos.models import MemoryLayer, MemoryRecord

Base = declarative_base()


class MemoryRecordORM(Base):
    __tablename__ = "memory_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String, nullable=True)
    layer = Column(String, nullable=False)
    scope = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    importance = Column(Float, nullable=False, default=0.5)
    decay = Column(Float, nullable=False, default=0.05)
    embedding = Column(JSON, nullable=True)
    content = Column(String, nullable=False, default="")
    record_metadata = Column(JSON, nullable=False, default=dict)

    def to_model(self) -> MemoryRecord:
        updated_at = self.updated_at or self.created_at
        return MemoryRecord(
            id=self.external_id or str(self.id),
            layer=self.layer,
            scope=self.scope,
            created_at=self.created_at or datetime.utcnow(),
            updated_at=updated_at or datetime.utcnow(),
            expires_at=self.expires_at,
            importance=float(self.importance),
            decay=float(self.decay),
            embedding=list(self.embedding or []),
            content=self.content,
            metadata=dict(self.record_metadata or {}),
        )

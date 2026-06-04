from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import declarative_base, declared_attr

from agent_memory_system.models import MemoryLayer, MemoryScope

Base = declarative_base()


class MemoryRecordORM(Base):
    __tablename__ = "memory_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(64), unique=True, index=True)
    layer = Column(String(20), index=True, nullable=False)
    scope = Column(String(20), index=True, nullable=False)
    created_at = Column(DateTime, index=True, nullable=False)
    updated_at = Column(DateTime, index=True, nullable=False)
    expires_at = Column(DateTime, index=True, nullable=True)
    importance = Column(Float, nullable=False, default=0.5)
    decay = Column(Float, nullable=False, default=0.05)
    embedding = Column(JSON, nullable=True)
    content = Column(String, nullable=False)
    record_metadata = Column("metadata", JSON, nullable=False, default=dict)

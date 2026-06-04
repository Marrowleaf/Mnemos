from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, Sequence

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from agent_memory_system.models import MemoryLayer, MemoryRecord
from agent_memory_system.store import Base, MemoryRecordORM


class MemoryStore:
    def __init__(self, database_url: str = "sqlite:///memory.db") -> None:
        self.engine = create_engine(database_url, future=True)
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            future=True,
        )
        Base.metadata.create_all(self.engine)

    def add(self, record: MemoryRecord) -> MemoryRecord:
        now = datetime.utcnow()
        record.updated_at = now
        if not record.created_at:
            record.created_at = now

        with self.SessionLocal() as session:
            orm = MemoryRecordORM(
                external_id=record.id,
                layer=record.layer.value,
                scope=record.scope.value,
                created_at=record.created_at,
                updated_at=record.updated_at,
                expires_at=record.expires_at,
                importance=float(record.importance),
                decay=float(record.decay),
                embedding=list(record.embedding or []),
                content=record.content,
            )
            session.add(orm)
            session.commit()
            session.refresh(orm)
            record.id = orm.external_id or str(orm.id)
            return record

    def get(self, record_id: str) -> MemoryRecord | None:
        with self.SessionLocal() as session:
            orm = (
                session.query(MemoryRecordORM)
                .filter(MemoryRecordORM.external_id == record_id)
                .one_or_none()
            )
            if not orm:
                return None
            updated_at = orm.updated_at or orm.created_at
            return MemoryRecord(
                id=orm.external_id or str(orm.id),
                layer=orm.layer,
                scope=orm.scope,
                created_at=orm.created_at,
                updated_at=updated_at,
                expires_at=orm.expires_at,
                importance=float(orm.importance),
                decay=float(orm.decay),
                embedding=list(orm.embedding or []),
                content=orm.content,
                metadata=dict(getattr(orm, "record_metadata", None) or {}),
            )

    def delete(self, record_id: str) -> bool:
        with self.SessionLocal() as session:
            orm = (
                session.query(MemoryRecordORM)
                .filter(MemoryRecordORM.external_id == record_id)
                .one_or_none()
            )
            if not orm:
                return False
            session.delete(orm)
            session.commit()
            return True

    def list_records(self, scope: Optional[str] = None) -> list[MemoryRecord]:
        with self.SessionLocal() as session:
            query = session.query(MemoryRecordORM)
            if scope:
                query = query.filter(MemoryRecordORM.scope == scope)
            rows: list[MemoryRecordORM] = query.all()
            out: list[MemoryRecord] = []
            for row in rows:
                updated_at = row.updated_at or row.created_at
                out.append(
                    MemoryRecord(
                        id=row.external_id or str(row.id),
                        layer=row.layer,
                        scope=row.scope,
                        created_at=row.created_at,
                        updated_at=updated_at,
                        expires_at=row.expires_at,
                        importance=float(row.importance),
                        decay=float(row.decay),
                        embedding=list(row.embedding or []),
                        content=row.content,
                        metadata=dict(getattr(row, "record_metadata", None) or {}),
                    )
                )
            return out

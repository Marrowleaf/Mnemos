from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, Sequence

from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session, sessionmaker

from mnemos.models import MemoryLayer, MemoryRecord
from mnemos.store import Base, MemoryRecordORM


def _utcnow() -> datetime:
    return datetime.utcnow()


class MemoryStore:
    def __init__(
        self,
        database_url: str = "sqlite:///memory.db",
        encrypt: bool = False,
    ) -> None:
        self.encrypt_default = bool(encrypt)
        self.engine = create_engine(database_url, future=True)
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            future=True,
        )
        Base.metadata.create_all(self.engine)

    def add(self, record: MemoryRecord) -> MemoryRecord:
        now = _utcnow()
        record.updated_at = now
        if not record.created_at:
            record.created_at = now

        with self.SessionLocal() as session:
            content = record.content or ""
            if self.encrypt_default:
                from mnemos.store import _encrypt
                content = _encrypt(content)
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
                content=content,
                record_metadata=dict(record.metadata or {}),
                encrypted="true" if self.encrypt_default else "false",
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
                .filter(
                    (MemoryRecordORM.external_id == record_id)
                    | (MemoryRecordORM.id == int(record_id))
                )
                .one_or_none()
            )
            if not orm:
                return None
            return orm.to_model()

    def delete(self, record_id: str) -> bool:
        with self.SessionLocal() as session:
            orm = (
                session.query(MemoryRecordORM)
                .filter(
                    (MemoryRecordORM.external_id == record_id)
                    | (MemoryRecordORM.id == int(record_id))
                )
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
            return [row.to_model() for row in rows]

    def prune_expired(self, *, before: Optional[datetime] = None) -> int:
        with self.SessionLocal() as session:
            when = before or _utcnow()
            stmt = delete(MemoryRecordORM).where(
                MemoryRecordORM.expires_at != None,
                MemoryRecordORM.expires_at <= when,
            )
            result = session.execute(stmt)
            session.commit()
            return int(result.rowcount)


__all__ = ["MemoryStore"]

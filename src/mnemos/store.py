from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, delete
from sqlalchemy.orm import Session, declarative_base

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
class MemoryStore:
    def __init__(self, database_url: str = "sqlite:///memory.db") -> None:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        self.engine = create_engine(database_url, future=True)
        self.SessionLocal = sessionmaker(
            bind=self.engine, expire_on_commit=False, future=True
        )
        Base.metadata.create_all(self.engine)

    def add(self, record: MemoryRecord) -> MemoryRecord:
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
                record_metadata=dict(record.metadata or {}),
            )
            session.add(orm)
            session.commit()
            session.refresh(orm)
            return orm.to_model()

    def get(self, record_id: str):
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

    def list_records(self, *, scope: Optional[str] = None):
        with self.SessionLocal() as session:
            query = session.query(MemoryRecordORM)
            if scope:
                query = query.filter(MemoryRecordORM.scope == scope)
            return [orm.to_model() for orm in query.order_by(MemoryRecordORM.id.desc())]

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

    def prune_expired(self, *, before: Optional[datetime] = None) -> int:
        with self.SessionLocal() as session:
            when = before or datetime.utcnow()
            stmt = delete(MemoryRecordORM).where(
                MemoryRecordORM.expires_at != None,
                MemoryRecordORM.expires_at <= when,
            )
            result = session.execute(stmt)
            session.commit()
            return int(result.rowcount)

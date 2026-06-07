from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, delete
from sqlalchemy.orm import Session, declarative_base

from mnemos.models import MemoryLayer, MemoryRecord

Base = declarative_base()

_ENCODING = "utf-8"


def _get_secret() -> bytes:
    raw = os.environ.get("MNEMOS_ENCRYPTION_KEY") or os.environ.get("MNEMOS_MASTER_KEY")
    if not raw:
        raise RuntimeError(
            "Encryption requested but MNEMOS_ENCRYPTION_KEY is not set"
        )
    normalized = raw.strip()
    if len(normalized) < 16:
        raise RuntimeError("MNEMOS_ENCRYPTION_KEY must be at least 16 characters")
    return hashlib.sha256(normalized.encode(_ENCODING)).digest()


def _encrypt(plaintext: str) -> str:
    key = _get_secret()
    nonce = os.urandom(12)
    out = hmac.new(key, nonce, hashlib.sha256).digest()[:16]
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    ciphertext = AESGCM(key).encrypt(nonce, plaintext.encode(_ENCODING), None)
    payload = base64.urlsafe_b64encode(nonce + out + ciphertext).decode("ascii")
    return f"enc:v1:{payload}"


def _decrypt(token: str) -> str:
    if not token.startswith("enc:v1:"):
        return token
    payload = base64.urlsafe_b64decode(token.split(":", 2)[2].encode("ascii"))
    nonce, mac_tag, ciphertext = payload[:12], payload[12:28], payload[28:]
    key = _get_secret()
    expected = hmac.new(key, nonce, hashlib.sha256).digest()[:16]
    if not hmac.compare_digest(mac_tag, expected):
        raise RuntimeError("Mnemos record MAC check failed")
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    return AESGCM(key).decrypt(nonce, ciphertext, None).decode(_ENCODING)


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
    encrypted = Column(String, nullable=False, default="false")

    def to_model(self) -> MemoryRecord:
        updated_at = self.updated_at or self.created_at
        content = self.content
        if str(self.encrypted) == "true":
            try:
                content = _decrypt(content)
            except RuntimeError:
                content = "[encrypted]"
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
            content=content,
            metadata=dict(self.record_metadata or {}),
        )


class MemoryStore:
    def __init__(self, database_url: str = "sqlite:///memory.db", encrypt: bool = False) -> None:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        self.encrypt_default = bool(encrypt)
        self.engine = create_engine(database_url, future=True)
        self.SessionLocal = sessionmaker(
            bind=self.engine, expire_on_commit=False, future=True
        )
        if "encrypted" not in [c.name for c in MemoryRecordORM.__table__.columns]:
            self._ensure_encrypted_column()

    def _ensure_encrypted_column(self) -> None:
        dialect_name = self.engine.dialect.name
        with self.engine.begin() as conn:
            if dialect_name == "sqlite":
                conn.exec_driver_sql(
                    "ALTER TABLE memory_records ADD COLUMN encrypted VARCHAR NOT NULL DEFAULT 'false'"
                )
            else:
                conn.exec_driver_sql(
                    "ALTER TABLE memory_records ADD COLUMN encrypted VARCHAR NOT NULL DEFAULT 'false'"
                )

    def _encrypt_text(self, text: str) -> str:
        return _encrypt(text) if self.encrypt_default else text

    def add(self, record: MemoryRecord) -> MemoryRecord:
        persisted_content = self._encrypt_text(record.content or "")
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
                content=persisted_content,
                record_metadata=dict(record.metadata or {}),
                encrypted="true" if self.encrypt_default else "false",
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

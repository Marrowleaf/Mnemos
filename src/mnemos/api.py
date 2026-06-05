from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Optional, Sequence

from mnemos.memory import MemoryStore
from mnemos.models import MemoryLayer, MemoryRecord, MemoryScope


class AgentMemoryAPI:
    def __init__(self, database_url: str = "sqlite:///memory.db") -> None:
        self.store = MemoryStore(database_url=database_url)

    def remember(
        self,
        text: str,
        layer: Optional[MemoryLayer] = None,
        scope: Optional[MemoryScope] = None,
        session_id: Optional[str] = None,
        importance: Optional[float] = None,
        tags: Optional[list[str]] = None,
        expires_in_hours: Optional[float] = None,
    ) -> MemoryRecord:
        metadata: dict[str, object] = {"sessionId": session_id} if session_id else {}
        if tags:
            metadata["tags"] = list(tags)
        record = MemoryRecord(
            content=text,
            layer=layer or MemoryLayer.WORKING,
            scope=scope or MemoryScope.SESSION,
            importance=float(importance) if importance is not None else 0.5,
            decay=0.05,
            embedding=[],
            expires_at=(
                datetime.utcnow() + timedelta(hours=expires_in_hours)
                if expires_in_hours is not None
                else None
            ),
            metadata=metadata,
        )
        return self.store.add(record)

    def recall(
        self,
        query: Optional[str] = None,
        *,
        layer: Optional[MemoryLayer] = None,
        scope: Optional[MemoryScope] = None,
        session_id: Optional[str] = None,
        limit: int = 10,
        tags: Optional[list[str]] = None,
        redact: bool = False,
    ) -> Sequence[MemoryRecord]:
        scope_value = scope.value if scope else None
        results = self.store.list_records(scope=scope_value)
        tag_set = {t.lower() for t in tags or []}
        scored: list[tuple[float, MemoryRecord]] = []
        for item in results:
            if query:
                query_lower = query.lower()
                text = (item.content or "").lower()
                if query_lower not in text:
                    continue
            if layer and item.layer != layer:
                continue
            if tag_set:
                item_tags = {str(t).lower() for t in ((item.metadata or {}).get("tags") or [])}
                if not (tag_set & item_tags):
                    continue
            score = float(item.importance or 0.0)
            scored.append((score, item))
        scored.sort(key=lambda pair: (pair[0], pair[1].created_at or datetime.min), reverse=True)
        out = [item for _, item in scored[:limit]]
        return (
            [self._maybe_redact(r, redact=True) for r in out]
            if redact
            else out
        )

    def forget(self, record_id: str) -> bool:
        try:
            return self.store.delete(record_id)
        except Exception:
            return False

    def prune_expired(self, *, before: Optional[datetime] = None) -> int:
        return self.store.prune_expired(before=before)

    def suggest_tags(self, *, limit: int = 10) -> list[str]:
        records = self.recall(query=None, limit=limit)
        tag_counts: dict[str, int] = {}
        for record in records:
            tags = ((record.metadata or {}).get("tags") or [])
            for tag in tags:
                key = str(tag).lower()
                tag_counts[key] = tag_counts.get(key, 0) + 1
        ranked = sorted(tag_counts.items(), key=lambda item: (item[1], item[0]), reverse=True)
        return [tag for tag, _ in ranked[:limit]]

    def export_snapshot(
        self,
        *,
        scope: Optional[MemoryScope] = None,
        layer: Optional[MemoryLayer] = None,
        tags: Optional[list[str]] = None,
        limit: int = 1000,
    ) -> str:
        records = self.recall(
            query=None,
            scope=scope,
            layer=layer,
            limit=limit,
            tags=tags,
            redact=False,
        )
        payload = []
        for record in records:
            data = record.model_dump(by_alias=True)
            data.setdefault("id", record.id)
            payload.append(data)
        return __import__("json").dumps(payload, default=str)

    def import_snapshot(
        self,
        payload: str,
        *,
        scope: Optional[MemoryScope] = None,
        layer: Optional[MemoryLayer] = None,
        merge: bool = False,
    ) -> dict:
        parsed = __import__("json").loads(payload)
        if not isinstance(parsed, list):
            raise ValueError("snapshot payload must be a list")
        created = 0
        skipped = 0
        for entry in parsed:
            tags = entry.get("metadata", {}).get("tags") if isinstance(entry.get("metadata"), dict) else None
            existing_id = entry.get("id")
            if existing_id and not merge:
                existing = self.store.get(str(existing_id))
                if existing:
                    skipped += 1
                    continue
            record = MemoryRecord(
                content=str(entry.get("content") or entry.get("summary") or ""),
                layer=layer or MemoryLayer(entry.get("layer", "working")),
                scope=scope or MemoryScope(entry.get("scope", "session")),
                importance=float(entry.get("importance", 0.5)),
                decay=float(entry.get("decay", 0.05)),
                embedding=list(entry.get("embedding") or []),
                metadata={"tags": list(tags)} if tags else {},
            )
            self.store.add(record)
            created += 1
        return {"created": created, "skipped": skipped}

    _PII_PATTERNS = (
        r"[A-Za-z0-9._%+\-]+@[A-Za-z-z0-9.\-]+\.[A-Za-z]{2,}",
        r"\b\+?\d{1,3}[-. (]*\d{3}[-. )]*\d{3}[-. ]*\d{4}\b",
        r"\b\d{3}[-.]\d{2}[-.]\d{4}\b",
        r"\b\d{3}-\d{2}-\d{4}\b",
        r"\b\d{4}[- ]\d{4}[- ]\d{4}[- ]\d{4}\b",
    )

    def _redact_text(self, text: str) -> str:
        value = text
        for pattern in self._PII_PATTERNS:
            value = re.sub(pattern, "[redacted]", value)
        return value

    def _maybe_redact(self, record: MemoryRecord, *, redact: bool) -> MemoryRecord:
        if not redact or not record.content:
            return record
        return MemoryRecord(
            **{
                **record.model_dump(by_alias=False),
                "content": self._redact_text(record.content),
            }
        )


__all__ = ["AgentMemoryAPI"]

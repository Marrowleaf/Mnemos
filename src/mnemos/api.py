from __future__ import annotations

import json
from datetime import datetime
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
        return [item for _, item in scored[:limit]]

    def forget(self, record_id: str) -> bool:
        try:
            return self.store.delete(record_id)
        except Exception:
            return False

    def prune_expired(self, *, before: Optional[datetime] = None) -> int:
        return self.store.prune_expired(before=before)

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
        )
        payload = []
        for record in records:
            data = record.model_dump(by_alias=True)
            data.setdefault("id", record.id)
            payload.append(data)
        return json.dumps(payload, default=str)

    def import_snapshot(
        self,
        payload: str,
        *,
        scope: Optional[MemoryScope] = None,
        layer: Optional[MemoryLayer] = None,
        merge: bool = False,
    ) -> dict:
        parsed = json.loads(payload)
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


__all__ = ["AgentMemoryAPI"]

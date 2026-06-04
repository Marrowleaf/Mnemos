from __future__ import annotations

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
    ) -> MemoryRecord:
        record = MemoryRecord(
            content=text,
            layer=layer or MemoryLayer.WORKING,
            scope=scope or MemoryScope.SESSION,
            importance=float(importance) if importance is not None else 0.5,
            decay=0.05,
            embedding=[],
            metadata={"sessionId": session_id} if session_id else {},
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
    ) -> Sequence[MemoryRecord]:
        scope_value = scope.value if scope else None
        results = self.store.list_records(scope=scope_value)
        scored: list[tuple[float, MemoryRecord]] = []
        for item in results:
            if query:
                query_lower = query.lower()
                text = (item.content or "").lower()
                if query_lower not in text:
                    continue
            if layer and item.layer != layer:
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


__all__ = ["AgentMemoryAPI"]

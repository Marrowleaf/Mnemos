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
        scope: Optional[MemoryScope] = None,
        session_id: Optional[str] = None,
        limit: int = 10,
    ) -> Sequence[MemoryRecord]:
        results = self.store.list_records(scope=scope.value if scope else None)
        scored = []
        for item in results:
            text = (item.content or "").lower()
            score = item.importance or 0.0
            if query:
                q = query.lower()
                if q in text:
                    score += 0.5
            scored.append((score, item))
        scored.sort(key=lambda pair: (pair[0], pair[1].created_at or datetime.min), reverse=True)
        return [item for _, item in scored[:limit]]

    def forget(self, record_id: str) -> bool:
        return self.store.delete(record_id)


__all__ = ["AgentMemoryAPI"]

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Iterable, Optional

from agent_memory_system.memory import MemoryStore
from agent_memory_system.models import MemoryLayer, MemoryRecord, MemoryScope


class AgentMemoryAPI:
    def __init__(self, store: Optional[MemoryStore] = None) -> None:
        self.store = store or MemoryStore()

    def _make_id(self, text: str, session_id: str) -> str:
        digest = hashlib.sha1(f"{session_id}:{text}".encode("utf-8")).hexdigest()[:12]
        return digest

    def remember(
        self,
        text: str,
        layer: MemoryLayer = MemoryLayer.WORKING,
        scope: MemoryScope = MemoryScope.SESSION,
        session_id: str = "default",
        importance: float = 0.5,
        decay: float = 0.05,
        metadata: Optional[dict] = None,
    ) -> MemoryRecord:
        record = MemoryRecord(
            id=self._make_id(text, session_id),
            layer=layer,
            scope=scope,
            importance=importance,
            decay=decay,
            content=text,
            metadata=metadata or {},
        )
        return self.store.add(record)

    def recall(
        self,
        query: str,
        session_id: str = "default",
        scope: Optional[MemoryScope] = None,
        limit: int = 10,
    ):
        from agent_memory_system.retrieval import MemoryRetriever

        retriever = MemoryRetriever(self.store)
        results = retriever.recall(query=query, scope=scope and scope.value, limit=limit)
        return [r.record for r in results]

    def forget(self, record_id: str) -> bool:
        return self.store.delete(record_id)

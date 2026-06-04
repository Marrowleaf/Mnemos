from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

from agent_memory_system.models import MemoryLayer, MemoryRecord


@dataclass
class RetrievalResult:
    record: MemoryRecord
    score: float


class RetrievalPolicy:
    def rank(self, record: MemoryRecord, now: datetime) -> float:
        raise NotImplementedError


class BasicRetrievalPolicy(RetrievalPolicy):
    def rank(self, record: MemoryRecord, now: datetime) -> float:
        age = (now - record.updated_at).total_seconds() / 3600.0
        age_penalty = 0.01 * max(age, 0.0)
        return record.importance - age_penalty


class MemoryRetriever:
    def __init__(self, store, policy: RetrievalPolicy | None = None) -> None:
        self.store = store
        self.policy = policy or BasicRetrievalPolicy()

    def recall(self, query: str, scope: str | None = None, limit: int = 10) -> Sequence[RetrievalResult]:
        raw = self.store.list_records(scope=scope)
        now = datetime.utcnow()
        scored = [
            RetrievalResult(record=record, score=self.policy.rank(record, now))
            for record in raw
        ]
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:limit]

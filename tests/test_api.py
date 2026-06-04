from __future__ import annotations

import pytest

from mnemos import AgentMemoryAPI, MemoryLayer, MemoryScope


@pytest.fixture()
def api():
    return AgentMemoryAPI(database_url="sqlite://")


def test_remember_returns_id(api):
    record = api.remember("hello-world")
    assert record.id
    assert record.content == "hello-world"


def test_recall_returns_results(api):
    api.remember("hello-world")
    hits = api.recall("hello")
    assert any("hello-world" in (item.content or "") for item in hits)


def test_recall_respects_scope(api):
    api.remember("session-only", scope=MemoryScope.SESSION)
    api.remember("user-scope", scope=MemoryScope.USER)
    session_hits = api.recall("session-only", scope=MemoryScope.SESSION)
    user_hits = api.recall("user-scope", scope=MemoryScope.USER)
    assert len(session_hits) >= 1
    assert len(user_hits) >= 1


def test_forget_removes_record(api):
    record = api.remember("to-delete")
    assert api.forget(record.id) is True
    assert api.forget(record.id) is False

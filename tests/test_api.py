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


def test_recall_empty_for_no_match(api):
    api.remember("unrelated")
    hits = api.recall("zzzz-no-match")
    assert hits == []


def test_forget_bad_id_returns_false(api):
    assert api.forget("does-not-exist") is False


def test_recall_respects_scope(api):
    api.remember("session-only", scope=MemoryScope.SESSION)
    api.remember("user-scope", scope=MemoryScope.USER)
    session_hits = api.recall("session-only", scope=MemoryScope.SESSION)
    user_hits = api.recall("user-scope", scope=MemoryScope.USER)
    assert len(session_hits) >= 1
    assert len(user_hits) >= 1


def test_recall_respects_layer(api):
    api.remember("semantic-fact", layer=MemoryLayer.SEMANTIC)
    api.remember("episodic-event", layer=MemoryLayer.EPISODIC)
    semantic_hits = api.recall("fact", layer=MemoryLayer.SEMANTIC)
    episodic_hits = api.recall("event", layer=MemoryLayer.EPISODIC)
    assert any("semantic-fact" in (r.content or "") for r in semantic_hits)
    assert any("episodic-event" in (r.content or "") for r in episodic_hits)


def test_recall_defaults_to_session_scope_when_none(api):
    api.remember("unspecified-scope")
    hits = api.recall("unspecified")
    assert len(hits) >= 1


def test_forget_returns_true_then_false(api):
    record = api.remember("to-delete")
    assert api.forget(record.id) is True
    assert api.forget(record.id) is False

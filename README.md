# Mnemos — Agent Memory System

**Mnemos** is a structured, SQLite-backed memory backend for AI agents. It stores durable facts, preferences, episodic events, and session context across runtime restarts — with scoped retrieval, tagging, TTL expiry, portable snapshots, and recall-time PII redaction.

Built for integration, not demonstration. Zero external services. Designed for production agent runtimes.

---

## Overview

Modern agents need memory that outlives a single process or session. Mnemos fills that gap with a clean Python API that supports:

- Hierarchical memory layers (`working`, `episodic`, `semantic`)
- Scope-aware retrieval (`session`, `user`, `agent`)
- First-class tagging with intersection filtering
- TTL-based expiry and background pruning
- Portable JSON snapshots for import/export
- Recall-time redaction of common PII patterns
- Auto-tag suggestions based on record frequency

It ships as an installable Python package and is already integrated into the Hermes agent runtime.

---

## Features

### Layered Memory
Records are organized into layers that reflect how humans and agents organize knowledge:

- `working` – transient, short-lived context
- `episodic` – time-bound events and interactions
- `semantic` – stable facts, preferences, and distilled knowledge

### Scoped Retrieval
Every memory has a scope that controls who or what can access it:

- `session` – confined to a single agent run or conversation
- `user` – tied to a specific user across sessions
- `agent` – shared across all sessions for a given agent

### Tagging and Filtering
Tags are stored in record metadata and resolved at recall time. Use tags to categorize, segment, or redact subsets of memory without changing the underlying store.

### TTL and Expiry
Temporal decay is handled explicitly. When storing a memory, supply `expires_in_hours` to define a TTL. Call `prune_expired()` to remove stale records in bulk.

### Import / Export Snapshots
Serialize any subset of memory to a portable JSON payload with `export_snapshot()`. Re-hydrate it into the same or a different store with `import_snapshot()`, with optional deduplication semantics.

### Recall-Time PII Redaction
Enable `redact=True` during recall to mask emails, phone numbers, SSNs, and payment card numbers before returning records. The raw data in the store is never modified.

### Auto-Tag Suggestions
Call `suggest_tags()` to retrieve the most frequent tags across recent high-importance records. Useful for auto-labeling, dashboards, or agent heuristics.

---

## Installation

```bash
pip install mnemos
```

Or install from source for development:

```bash
git clone https://github.com/Marrowleaf/Mnemos.git
cd Mnemos
pip install -e .
```

Run tests:

```bash
pytest
```

---

## Quick Start

```python
from mnemos import AgentMemoryAPI, MemoryLayer, MemoryScope

api = AgentMemoryAPI()

# Store a semantic fact about the user
api.remember(
    "James prefers Tailscale for remote access.",
    layer=MemoryLayer.SEMANTIC,
    scope=MemoryScope.USER,
    tags=["infrastructure", "preferences"],
    importance=0.9,
)

# Recall with scope and tag filtering
results = api.recall(
    "remote access",
    scope=MemoryScope.USER,
    tags=["infrastructure"],
)

# Recall with PII redaction
safe_results = api.recall(
    "contact",
    scope=MemoryScope.USER,
    redact=True,
)

# Store a time-limited working context
api.remember(
    "Pending PR review: #382 on odysseus",
    layer=MemoryLayer.WORKING,
    scope=MemoryScope.SESSION,
    expires_in_hours=4,
    tags=["github", "review"],
)

# Auto tag suggestions
suggested = api.suggest_tags(limit=5)

# Prune expired records
removed = api.prune_expired()

# Snapshot and restore
snapshot = api.export_snapshot(scope=MemoryScope.USER)
api.import_snapshot(snapshot, merge=True)
```

---

## API Reference

### `AgentMemoryAPI(database_url: str = "sqlite:///memory.db")`

Primary interface for memory operations. Defaults to a local SQLite database if none is provided.

**`remember(text, layer, scope, session_id, importance, tags, expires_in_hours)`**
Persist a new memory record. Returns the saved `MemoryRecord`.

**`recall(query, *, layer, scope, session_id, limit, tags, redact)`**
Retrieve matching records sorted by importance and recency.

**`forget(record_id)`**
Delete a record by its identifier.

**`prune_expired(before)`**
Remove expired records. Returns the count of deletions.

**`suggest_tags(limit)`**
Return the most frequent tags from recent high-importance records.

**`export_snapshot(scope, layer, tags, limit)`**
Serialize records to JSON for backup or transfer.

**`import_snapshot(payload, scope, layer, merge)`**
Import a JSON snapshot. `merge=False` skips already-existing IDs; `merge=True` re-imports every record.

---

## Design Notes

- **SQLite-first**: Zero external services. A single file contains the entire store.
- **No mutable secrets**: PII redaction acts on returned records only; the stored copy is immutable.
- **Composable**: Layers, scopes, tags, and expiry can be combined freely.
- **Tested**: Core behaviors are covered by pytest.

---

## Integration

Mnemos is the active memory backend for the Hermes agent runtime, exposed via the `mnemos_remember`, `mnemos_recall`, and `mnemos_forget` tools. If you want to wire it into your own agent, use `AgentMemoryAPI` directly.

---

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Add tests for new behavior.
4. Run `pytest` before submitting.
5. Open a pull request.

See the issue tracker for labeled good-first-issues.

---

## License

MIT

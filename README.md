# Mnemos

Mnemos is an integrated memory system for AI agents. It stores durable facts, preferences, and episodic events in a structured SQLite-backed store that can be read, recalled, and forgotten at runtime.

## Capabilities
- Layered memory: `working`, `episodic`, `semantic`
- Scoped retrieval: `session`, `user`, `agent`
- Tagged records with recall-time filtering
- TTL-aware expiry and pruning
- Structured import/export snapshots
- Recall-time PII redaction for sensitive data
- Auto-tagging suggestions

## Status
- Importable Python package
- Remember / recall / forget verified end to end
- TTL pruning, tags, import/export, auto-tagging, and redaction included
- Intended for direct integration as an agent memory backend

## Install
```bash
pip install mnemos
```

## Usage
```python
from mnemos import AgentMemoryAPI, MemoryLayer, MemoryScope

api = AgentMemoryAPI()
api.remember("Project uses Tailscale", layer=MemoryLayer.SEMANTIC, scope=MemoryScope.USER)
results = api.recall("Which tunnel does James prefer?", scope=MemoryScope.USER)
api.forget(results[0].id)
results = api.recall("James", scope=MemoryScope.USER, redact=True)
tags = api.suggest_tags()
snapshot = api.export_snapshot()
api.import_snapshot(snapshot, merge=True)
api.prune_expired()
```

### Redaction
Use `recall(..., redact=True)` to mask common PII patterns including emails, phone numbers, SSNs, and card numbers before returning results.

## Repository
- Developer: Marrowleaf
- GitHub: https://github.com/Marrowleaf/Mnemos

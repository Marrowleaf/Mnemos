# Mnemos

Mnemos is an integrated memory system for AI agents. It stores durable facts, preferences, and episodic events in a structured SQLite-backed store that can be read, recalled, and forgotten at runtime.

## Capabilities
- Layered memory: `working`, `episodic`, `semantic`
- Scoped retrieval: `session`, `user`, `agent`
- Tagged records with recall-time filtering
- TTL-aware expiry and pruning
- Structured import/export snapshots
- Modeled API surface for embedding into agent runtimes

## Status
- Importable Python package
- Remember / recall / forget verified end to end
- TTL pruning, tags, import/export, and snapshot tooling included
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
```

## Repository
- Developer: Marrowleaf
- GitHub: https://github.com/Marrowleaf/Mnemos

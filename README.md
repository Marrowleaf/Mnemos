# Agent Memory System

Lightweight layered memory for AI agents:
- layers: `working`, `episodic`, `semantic`
- scopes: `session`, `user`, `agent`
- storage: SQLite via SQLAlchemy
- operations: remember, recall, forget

```python
from agent_memory_system import AgentMemoryAPI, MemoryLayer, MemoryScope

api = AgentMemoryAPI()
api.remember("James prefers Tailscale tunnels", layer=MemoryLayer.SEMANTIC, scope=MemoryScope.USER)
results = api.recall("Which tunnel does James prefer?", scope=MemoryScope.USER)
api.forget(results[0].id)
```

## Install
```bash
pip install -e .
```

## Status
- 0.1.0 prototype
- add/get/delete/recall implemented
- no external dependencies beyond pydantic, sqlalchemy, numpy

## Test
```bash
PYTHONPATH=src python - <<'PY'
from agent_memory_system import AgentMemoryAPI, MemoryLayer, MemoryScope
api = AgentMemoryAPI()
api.remember("test", layer=MemoryLayer.WORKING, scope=MemoryScope.SESSION)
print(api.recall("test"))
PY
```

## Repository
- developer: Marrowleaf
- GitHub: [Marrowleaf/agent-memory-system](https://github.com/Marrowleaf/agent-memory-system)

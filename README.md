# Agent Memory System

Lightweight layered memory for AI agents:
- layers: `working`, `episodic`, `semantic`
- scopes: `session`, `user`, `agent`
- storage: SQLite via SQLAlchemy
- retrieval: policy-ranked recall with simple decay/importance

```python
from agent_memory_system import AgentMemoryAPI, MemoryLayer, MemoryScope

api = AgentMemoryAPI()
api.remember("James prefers Tailscale tunnels", layer=MemoryLayer.SEMANTIC, scope=MemoryScope.USER)
results = api.recall("Which tunnel does James prefer?")
```

## Install
```bash
pip install -e .
```

## Status
- 0.1.0 prototype
- add/get/delete/recall implemented
- no external dependencies beyond pydantic, sqlalchemy, numpy

# Mnemos

Minimal layered memory for AI agents:
- layers: `working`, `episodic`, `semantic`
- scopes: `session`, `user`, `agent`
- storage: SQLite via SQLAlchemy
- operations: remember, recall, forget, decay

**Status**
- Imports verified
- Remember/recall/forget smoke-tested

## Install
```bash
pip install mnemos
```

Or editable:
```bash
git clone https://github.com/Marrowleaf/Mnemos.git
cd Mnemos
pip install -e .
```

## Usage
```python
from mnemos import AgentMemoryAPI, MemoryLayer, MemoryScope

api = AgentMemoryAPI()
api.remember("James prefers Tailscale tunnels", layer=MemoryLayer.SEMANTIC, scope=MemoryScope.USER)
results = api.recall("Which tunnel does James prefer?", scope=MemoryScope.USER)
api.forget(results[0].id)
```

## Repository
- developer: Marrowleaf
- GitHub: [Marrowleaf/Mnemos](https://github.com/Marrowleaf/Mnemos)
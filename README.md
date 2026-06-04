# Mnemos

Minimal layered memory for AI agents:
- layers: `working`, `episodic`, `semantic`
- scopes: `session`, `user`, `agent`
- storage: SQLite via SQLAlchemy
- operations: remember, recall, forget, decay

**Status**
- Imports verified
- Remember/recall/forget smoke-tested
- 8 pytest cases passing
- Active Hermes memory provider plugin shipped at `/usr/local/lib/hermes-agent/plugins/memory/mnemos/`

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

## Hermes integration
- Config: `memory.provider: mnemos` in `/root/.hermes/config.yaml`
- Plugin: `mnemos` under Hermes memory provider plugins
- Tools exposed: `mnemos_remember`, `mnemos_recall`, `mnemos_forget`

## Repository
- developer: Marrowleaf
- GitHub: [Marrowleaf/Mnemos](https://github.com/Marrowleaf/Mnemos)

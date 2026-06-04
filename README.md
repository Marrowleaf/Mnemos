[![CI](https://github.com/Marrowleaf/agent-memory-system/actions/workflows/ci.yml/badge.svg)](https://github.com/Marrowleaf/agent-memory-system/actions/workflows/ci.yml)
[![Coverage](https://raw.githubusercontent.com/Marrowleaf/agent-memory-system/main/assets/coverage-badge.svg)](https://github.com/Marrowleaf/agent-memory-system/actions)

**Agent Memory System** — a layered, schema-aware memory layer for AI agents with formal write/read protocols, compaction, and hierarchical payloads.

[GitHub](https://github.com/Marrowleaf/agent-memory-system) · [Issues](https://github.com/Marrowleaf/agent-memory-system/issues) · [Changelog](./CHANGELOG.md)

## Why this exists

Existing agent memory tools are built as specific integrations (Mem0, Zep, Letta). This package is built as a **protocol + storage layer** other systems can adopt: consistent memory semantics, relationship-aware operations, and a stable operator vocabulary.

## Key ideas

- Three memory layers with explicit flow between them
- Formal write/read queries with idempotent upserts
- Compaction policy for memory under pressure
- Hierarchical payload format agents can use without lock-in

## Quick start

```bash
git clone https://github.com/Marrowleaf/agent-memory-system.git
cd agent-memory-system
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Development

- Run tests: `pytest -q`
- Lint: `ruff check src tests`
- Format: `ruff format src tests`

## Status

- Package: `agent_memory_system`
- Python: `>=3.11`
- License: MIT

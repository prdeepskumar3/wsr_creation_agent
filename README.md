# WSR Creation Agent

WSR Creation Agent is a monorepo for AI-assisted weekly status report creation.

## Package Management

Python dependencies are managed with `uv` from the repository root.

```bash
uv sync --all-packages --all-groups
uv run pytest
```

Frontend dependencies are managed from `frontend/package.json`.

```bash
npm --prefix frontend install
npm --prefix frontend run dev
```

## Workspace Layout

- `backend/`: FastAPI API, services, domain rules, persistence, workers.
- `agent/`: LangChain/LangGraph workflows, prompts, retrieval, structured outputs.
- `shared/`: shared contracts and generated API artifacts.
- `frontend/`: Vite + React + TypeScript UI.
- `infra/`: deployment and local infrastructure assets.


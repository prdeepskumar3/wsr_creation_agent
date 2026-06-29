.PHONY: setup lock test lint typecheck backend-dev frontend-dev

setup:
	uv sync --all-packages --all-groups
	npm --prefix frontend install

lock:
	uv lock

test:
	uv run pytest

lint:
	uv run ruff check backend agent shared
	npm --prefix frontend run lint

typecheck:
	uv run mypy backend/src agent/src shared/src
	npm --prefix frontend run typecheck

backend-dev:
	uv run uvicorn main:app --app-dir backend/src --reload

frontend-dev:
	npm --prefix frontend run dev


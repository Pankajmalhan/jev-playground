# Run `make help` to see everything.
PY := backend/.venv/bin/python

.PHONY: help setup dev api web build run clean

help:
	@echo "make setup   install backend (uv) and frontend (npm) dependencies"
	@echo "make dev     API on :8000 and Vite on :5173 with hot reload (open :5173)"
	@echo "make build   build React into backend/static"
	@echo "make run     build, then serve everything from FastAPI on :8000"

setup:
	cd backend && uv venv .venv && uv pip install -r requirements.txt
	cd frontend && npm install
	@test -f .env || cp .env.example .env

api:
	cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000

web:
	cd frontend && npm run dev

dev:
	@$(MAKE) -j2 api web

build:
	cd frontend && npm run build

run: build
	cd backend && .venv/bin/uvicorn app.main:app --port 8000

clean:
	rm -rf backend/static frontend/node_modules backend/.venv

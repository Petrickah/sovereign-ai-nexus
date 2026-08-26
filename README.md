# Sovereign AI Nexus

## Overview

A small, self-hosted AI chat + artifact web app — a FastAPI/PostgreSQL backend, a React/TypeScript frontend, and an LLM layer that delegates to existing tooling instead of adding new metered API costs. Backend + AI Platform Engineering portfolio project, built incrementally.

## Status

v1 complete — chat with persisted history, full conversation CRUD, and a working Docker Compose stack end-to-end. Built incrementally, in the open, no fixed timeline.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose (bundled with recent Docker Desktop/Engine).
- A Claude Code OAuth token — run `claude setup-token` (requires the [Claude Code CLI](https://docs.claude.com/en/docs/claude-code) installed locally) and copy the token it prints.

## Setup

1. Copy the example environment file and fill in your own values:
   ```
   cp .env.example .env
   ```
   `.env` needs:
   - `DATABASE_USER` / `DATABASE_PASSWORD` / `DATABASE_NAME` / `DATABASE_PORT` — Postgres credentials for the bundled `database` container (any values work for local use; Postgres creates the database on first boot).
   - `CLAUDE_CODE_OAUTH_TOKEN` — the token from `claude setup-token` above. This is what lets the backend delegate chat requests to the `claude` CLI running inside its container.
   - `FRONTEND_ORIGIN` — the origin the backend accepts cross-origin requests from (defaults to `http://localhost:3000`, i.e. the Dockerized frontend's published port). Only change this if you're exposing the stack on a different host/port.

2. Start the stack:
   ```
   docker compose up -d --build
   ```
   This builds and starts four services:
   - `frontend` — the chat UI, served at [http://localhost:3000](http://localhost:3000).
   - `backend` — the FastAPI API, at [http://localhost:8000](http://localhost:8000).
   - `database` — PostgreSQL, not exposed outside the Docker network.
   - `adminer` — a database admin UI, at [http://localhost:8080](http://localhost:8080) (server: `database`, using the same credentials as `.env`).

3. Open [http://localhost:3000](http://localhost:3000) and start chatting. History is loaded on page load and persists across refreshes and restarts (Postgres data lives in a named volume).

## Usage

The backend exposes:

| Method | Path | Description |
|---|---|---|
| `POST` | `/chat` | Send a prompt, get back the assistant's response (persisted as one exchange). |
| `GET` | `/history` | List every stored prompt/response exchange, oldest first. |
| `DELETE` | `/history/{id}` | Delete a single exchange by id. |
| `DELETE` | `/history` | Delete the entire conversation history. |

The frontend UI covers all of this: sending a message, deleting a single exchange, and clearing the whole conversation (behind a confirmation step, since it can't be undone).

See `CLAUDE.md` for architecture notes, known gotchas, and the CI/CD setup.

<!-- This is a Kanban Board file created with MD Kanban extension -->
<!-- GitHub: https://github.com/jebakumarj/md-kanban -->
<!-- VS Code Extension: Search "MD Kanban" in the extension store (ID: jeddak.md-kanban) -->
<!-- Tracks movement only (Backlog/In Progress/Paused/Done), same philosophy as 05_Projects/KANBAN.md in the vault. Full task detail (Goal/Visible output/Done when) lives in CLAUDE.md and the private vault note — don't duplicate it here. -->

# Sovereign AI Nexus — Kanban

## Backlog

#### Task 2 — Schema PostgreSQL + model SQLAlchemy
<!-- id: task-1787230831000-0 -->
Tabela `exchanges` (prompt, response, created_at). Deliberately split from Task 1's original scope — Postgres isn't in docker-compose.yml yet.
Tags: `backend` `db`

#### Task 3 — Endpoint FastAPI POST /chat
<!-- id: task-1787230831000-1 -->
Delegates to `claude -p` (subprocess) or OpenRouter, env-switchable. Decide async subprocess handling + CLI auth-in-container before starting (flagged by council review) — see CLAUDE.md.
Tags: `backend` `api`

#### Task 4 — UI React/TS, chat input
<!-- id: task-1787230831000-2 -->
Input + submit, calls /chat, shows raw response first.
Tags: `frontend`

#### Task 5 — Render artifact (markdown)
<!-- id: task-1787230831000-3 -->
Format the response instead of raw JSON.
Tags: `frontend`

#### Task 6 — End-to-end wiring via Docker Compose
<!-- id: task-1787230831000-4 -->
Full flow (frontend -> backend -> LLM -> Postgres -> frontend) from a clean clone, `docker compose up` only.
Tags: `infra`

#### Task 7 — README
<!-- id: task-1787230831000-5 -->
Document local run instructions.
Tags: `docs`

## In Progress

## Paused

## Done

#### Task 1 — Scaffold repo + Docker Compose
<!-- id: task-1787230831000-6 -->
Backend (FastAPI/uvicorn, `uv`) + frontend (React/Vite/TS) scaffolds, hot-reload confirmed live end-to-end. Postgres deliberately deferred to Task 2. Four real bugs found and fixed along the way (see CLAUDE.md "Gotchas" — hot-reload mount path, pnpm global bin PATH, frontend volume clobbering `dist/`, Kaniko vs. BuildKit `RUN --mount`, `uv.lock` wrongly gitignored).
Tags: `backend` `frontend` `infra`

#### CI/CD wiring (materialization + Jenkinsfile)
<!-- id: task-1787230831000-7 -->
Not a numbered task in the original breakdown, but a real prerequisite: Gitea repo (auto_init:false, clean signed initial commit), Jenkins multibranch job, per-service Kaniko build stages (backend + frontend, separate images — not separate Jenkins jobs), GitHub mirror via a dedicated SSH deploy key (Jenkins credential, "Mirror to GitHub" stage before the Docker build so mirroring never depends on build success). `dev` branch active. Verified end-to-end 2026-08-20: build SUCCESS, both images in the registry, both branches mirrored with signatures intact.
Tags: `infra` `ci-cd`

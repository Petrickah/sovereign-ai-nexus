<!-- This is a Kanban Board file created with MD Kanban extension -->
<!-- GitHub: https://github.com/jebakumarj/md-kanban -->
<!-- VS Code Extension: Search "MD Kanban" in the extension store (ID: jeddak.md-kanban) -->

# Sovereign AI Nexus — Kanban

## Backlog

#### Task 6 — End-to-end wiring via Docker Compose
<!-- id: task-1787230831000-4 -->
Full flow (frontend -> backend -> LLM -> Postgres -> frontend) from a clean clone, `docker compose up` only. Known blocker, decide before starting: no CORS middleware on the backend, and the Docker frontend (static `serve -s dist`, no dev proxy) 404s/falls through to SPA on `/chat` — fork between adding CORS vs. a reverse proxy in front of both services, see CLAUDE.md.
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

#### Task 2 — Schema PostgreSQL + model SQLAlchemy
<!-- id: task-1787230831000-0 -->
Tabela `exchanges` (prompt, response, created_at) live în `docker-compose.yml`, `DatabaseClient` cu client global (nu recreat per-request) + volum persistent, confirmat cu restart real al containerului.
Tags: `backend` `db`

#### Task 3 — Endpoint FastAPI POST /chat
<!-- id: task-1787230831000-1 -->
Delegare reală către `claude -p` (subprocess async, `/root/.claude` persistent via `CLAUDE_CODE_OAUTH_TOKEN`, workspace minimal `/workspace`), context de conversație din ultimele 30 schimburi, persistat în `exchanges`. Trei bug-uri reale găsite și reparate, verificate live: SQL cu paranteze în jurul coloanelor (întorcea un tip compus, nu coloane separate — crash confirmat din traceback la al doilea request), `created_at` prins după apelul LLM în loc de înainte (ordinea de evaluare a argumentelor kwargs în Python), și ordinea greșită a istoricului în context (ASC+reversed combinate greșit, apoi corectat la DESC+reversed) — confirmat corect cu un test live care cerea LLM-ului să repete istoricul.
Tags: `backend` `api`

#### Task 4 — UI React/TS, chat input
<!-- id: task-1787230831000-2 -->
ChatInput/ChatHistory, input controlat, Enter trimite, Shift+Enter linie nouă, disabled cât timp răspunsul e în așteptare. Implementat printr-o sesiune Claude Code separată, deschisă direct în repo — verificat cu browser headless real, tsc + eslint curate.
Tags: `frontend`

#### Task 5 — Render artifact (markdown)
<!-- id: task-1787230831000-3 -->
`react-markdown` + `remark-gfm` pentru răspunsurile assistant-ului (headings/liste/cod randate real, nu text brut); mesajele utilizatorului rămân text simplu. Dev proxy Vite (`/chat` → `:8000`) doar pentru `pnpm dev` local, fără efect pe build-ul Docker.
Tags: `frontend`

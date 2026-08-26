<!-- This is a Kanban Board file created with MD Kanban extension -->
<!-- GitHub: https://github.com/jebakumarj/md-kanban -->
<!-- VS Code Extension: Search "MD Kanban" in the extension store (ID: jeddak.md-kanban) -->

# Sovereign AI Nexus — Kanban

## Backlog

#### Task 9 — Deployment stage (K3s) + articol 5
<!-- id: task-1787230831000-10 -->
Ridicat 2026-08-26, la promovarea episodului 4: Jenkins-ul construiește și împinge imagini în registry, dar nu face niciun deployment real încă — arhitectura era deja decisă în nota din vault („Metodologia de lucru" → „Deployment": namespace-uri `dev`/`main` pe k3s), doar nescrisă în `Jenkinsfile`. Un pas `kubectl apply` nou, după `Build & Push`. Neînceput, nescopat în detaliu — de descompus abia când chiar începe.
Tags: `infra` `k8s`

## In Progress

## Paused

## Done

#### Task 8 — Unit tests (backend + frontend)
<!-- id: task-1787230831000-8 -->
Backend: pytest against the real FastAPI app + a disposable Postgres (`docker-compose.test.yml`, deliberately not SQLite — the raw-SQL dialect fidelity matters, see Gotchas). `DatabaseClient` gained a `DATABASE_HOST` env var (default `database`, unchanged for dev/prod) so tests can point it at localhost. `call_llm` mocked via `monkeypatch`, never shells out for real. Regression tests written to actually catch the two known bugs (composite-column SELECT, `created_at` captured after the LLM call) — verified live by reintroducing each bug and confirming the test fails, then reverting. Also found and fixed a real test-fixture deadlock along the way: `DatabaseClient`'s read methods never commit/close their implicit transaction, so a prior test's SELECT can leave the connection idle-in-transaction holding a lock that blocks the next test's `TRUNCATE` — only surfaced against real Postgres. Frontend: Vitest + RTL, global `fetch` mocked, App-level integration tests (send/render, per-exchange delete, clear-all cancel/confirm) plus a `ChatInput` keyboard/disabled-state unit test. Wired into `Jenkinsfile` as `Test: backend`/`Test: frontend` stages (Postgres + node sidecars in the same Kubernetes pod as `kaniko`) before the build stages — not yet verified against a real Jenkins run.
Tags: `backend` `frontend` `testing`

#### Task 6 — End-to-end wiring via Docker Compose
<!-- id: task-1787230831000-4 -->
Resolved the CORS-vs-proxy fork with `CORSMiddleware`, scoped to `FRONTEND_ORIGIN` (env-configurable) — smaller than a reverse proxy given public deploy is still out of scope. Frontend `Dockerfile` now bakes `VITE_API_BASE_URL` at build time (no dev-proxy equivalent for the static `serve -s dist` build). Full flow (frontend -> backend -> LLM -> Postgres -> frontend) confirmed working from a clean `docker compose up`.
Tags: `infra`

#### Task 7 — README
<!-- id: task-1787230831000-5 -->
Rewritten for a from-scratch setup: prerequisites, `.env` walkthrough, `docker compose up`, and an endpoint table. Someone who's never seen the repo can start it from the README alone.
Tags: `docs`

#### Conversation history CRUD
<!-- id: task-1787230831000-9 -->
Pulled forward from the deferred non-goals list (2026-08-26). `GET /history`, `DELETE /history/{id}`, `DELETE /history` + `DatabaseClient` methods; frontend loads history on mount, per-exchange delete, clear-all behind a confirmation step. Verified both by the implementing session and manually by Tiberiu in a live browser.
Tags: `backend` `frontend`

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

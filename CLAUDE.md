# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status (updated 2026-08-20)

Early scaffold stage. Backend (FastAPI/uvicorn via `uv`) and frontend (React/Vite/TS) both build, run, and have working hot-reload/dev loops — confirmed live, not just theoretical. No database, no `/chat` endpoint, no real chat UI yet. See `KANBAN.md` for a live per-task view (Backlog/In Progress/Done); full task detail (Goal/Visible output/Done when for each task) lives in a private vault note outside this repo — ask if you need that context, don't assume it's summarized correctly here.

Working branch is `dev` (manual commits, day-to-day work); `main` tracks stable/"production" state, updated only via an explicit merge. Both mirror to GitHub automatically on every push — nothing in this repo needs to stay private, unlike the sibling `blog` project.

## Commands

- `docker compose up -d --build` — start backend (`:8000`) + frontend (`:3000`).
- `docker compose build backend` / `... frontend` — rebuild one service.
- Backend hot-reload works through the container (`./backend/core:/code/core` volume mount + `uvicorn --reload`) — edit `backend/core/*.py` on the host, no rebuild needed.
- **Frontend does NOT hot-reload through Docker** — the frontend container serves a static production build (`pnpm build` at image-build time → `pnpm exec serve -s dist`), not a dev server. For fast frontend iteration, run `pnpm dev` directly on the host inside `frontend/` (Vite's own HMR, faster than anything Docker-mediated) — don't try to add a volume mount to "fix" this, it was tried and it breaks the build (see Gotchas).

## Architecture

Python (FastAPI) + PostgreSQL backend (Postgres not wired up yet — deliberately deferred, see `KANBAN.md` Task 2), React/TypeScript (Vite) frontend, Docker Compose for local dev. LLM calls delegate to existing tooling (Claude Code CLI via subprocess, or OpenRouter) rather than a metered Anthropic API key — no API key config exists yet, this lands with the `/chat` endpoint (Task 3).

## Gotchas (found 2026-08-20 — read before touching Docker/CI here)

- **Kaniko (this repo's actual CI builder) does not support BuildKit `RUN --mount` syntax** — silently ignored, not an error, so `uv`'s own official Docker recipe (`RUN --mount=type=bind,source=uv.lock,...`) fails with a confusing "No pyproject.toml found" instead of a clear "unsupported syntax" error. It builds fine locally (Docker Desktop/Engine defaults to BuildKit) but fails on Jenkins. Keep `backend/Dockerfile` on plain `COPY` — don't reintroduce `--mount` even if a tutorial/AI suggests it.
- **`backend/uv.lock` must be tracked in git** — it was briefly gitignored by a default `uv init`-style `.gitignore` (meant for libraries, not applications), which broke `uv sync --frozen` in CI. If a lockfile-related build failure shows up again, check `git ls-files` includes it before debugging further.
- **Docker Compose volume mounts must target where the app actually imports from, not a generic convention path.** The backend mount is `./backend/core:/code/core` — matches `WORKDIR /code` + `uvicorn core.main:app`. An earlier version mounted to `/code/app` (copied from a generic FastAPI tutorial) — silently broke hot-reload, since nothing ever read that path.
- **Don't add a volume mount to the frontend service.** It runs a built static bundle (`serve -s dist`), not a dev server — mounting host source over `/app` clobbers the built `dist/` and `node_modules` baked into the image, causing 404s. For frontend dev iteration, run `pnpm dev` on the host instead.
- **pnpm global installs don't work in this Docker image** (`pnpm add -g <pkg>` fails — pnpm's global bin dir isn't in `PATH` inside the container, and there's no interactive shell for `pnpm setup` to fix it). Add packages as normal (non-global) dependencies and invoke via `pnpm exec <pkg>`.

## CI/CD

Gitea (source of truth) → Jenkins multibranch (`Jenkinsfile`): checkout → mirror to GitHub (SSH deploy key, `github-mirror-sovereign-ai-nexus` Jenkins credential, write-scoped to this repo only via a GitHub Deploy Key — not a broader PAT) → Kaniko build **per service** (`backend` and `frontend` are separate stages in the same pipeline, each with its own context/Dockerfile/image tag — not separate Jenkins jobs; one stage failing doesn't block the other) → push to the private registry. The mirror stage runs before the build stages, independent of build success. `main` and `dev` both mirror automatically; no manual promotion step.

Deployment to a running environment (k3s namespaces for staging/prod) isn't wired up yet — deliberately deferred until there's a database and a real endpoint worth deploying, not just this skeleton.

## Non-goals (v1 — see the private vault note for the full list/reasoning)

No auth/OAuth/JWT, no conversation history CRUD, no multi-panel UI, no multi-agent orchestration, no public deploy yet. Don't add these without checking the vault note first — several were deliberately excluded to keep scope small (this project's whole premise is avoiding the scope-creep that killed its two predecessor project ideas).

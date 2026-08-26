# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status (updated 2026-08-26)

v1 complete, including Task 8: Postgres (global `DatabaseClient`, `lifespan`-managed), `POST /chat` delegating to `claude -p` with real conversation history, a working chat UI (`react-markdown`+`remark-gfm` rendering), full Docker Compose wiring (CORS-based, see "CORS" below), a from-scratch README, conversation history CRUD (`GET /history`, `DELETE /history/{id}`, `DELETE /history`, both backend + frontend), and a unit test suite (backend pytest against a real disposable Postgres, frontend Vitest/RTL with `fetch` mocked — see "Testing" below) so an agent can verify a change without Playwright/a real browser. Full task detail (Goal/Visible output/Done when for each task) lives in a private vault note outside this repo — ask if you need that context, don't assume it's summarized correctly here.

### CORS (Task 6 resolution)

The dev-only Vite proxy (`vite.config.ts`, `/chat`/`/history` → `:8000`) only exists for `pnpm dev`. The Docker frontend is a static build (`serve -s dist`) with no equivalent, so the backend has `CORSMiddleware` scoped to `FRONTEND_ORIGIN` (env-configurable, defaults to `http://localhost:3000`) instead — chosen over a reverse proxy since public deploy is still out of scope; revisit if that changes. The frontend's own Dockerfile bakes `VITE_API_BASE_URL` in at build time for the same reason (no dev-proxy equivalent in the static build).

Working branch is `dev` (manual commits, day-to-day work); `main` tracks stable/"production" state, updated only via an explicit merge. Both mirror to GitHub automatically on every push — nothing in this repo needs to stay private, unlike the sibling `blog` project.

## Commands

- `docker compose up -d --build` — start backend (`:8000`) + frontend (`:3000`).
- `docker compose build backend` / `... frontend` — rebuild one service.
- Backend hot-reload works through the container (`./backend/core:/code/core` volume mount + `uvicorn --reload`) — edit `backend/core/*.py` on the host, no rebuild needed.
- **Frontend does NOT hot-reload through Docker** — the frontend container serves a static production build (`pnpm build` at image-build time → `pnpm exec serve -s dist`), not a dev server. For fast frontend iteration, run `pnpm dev` directly on the host inside `frontend/` (Vite's own HMR, faster than anything Docker-mediated) — don't try to add a volume mount to "fix" this, it was tried and it breaks the build (see Gotchas).

## Testing

- Backend: `docker compose -f docker-compose.test.yml up -d --wait` (disposable Postgres on host port 5433, separate from the dev stack's `database` service — never run tests against dev data), then from `backend/`: `DATABASE_HOST=localhost DATABASE_PORT=5433 DATABASE_USER=test DATABASE_PASSWORD=test DATABASE_NAME=test uv run pytest -v`. Tear down after with `docker compose -f docker-compose.test.yml down -v` from the repo root.
- Frontend: `pnpm test` from `frontend/` (Vitest + React Testing Library, `fetch` mocked — no backend needed).
- Both wired into `Jenkinsfile` as `Test: backend`/`Test: frontend` stages (Postgres + node sidecar containers in the same Kubernetes pod as `kaniko`), before the `Build & Push` stages — written 2026-08-26, not yet verified against a real Jenkins run.
- `DatabaseClient` takes a `DATABASE_HOST` env var (default `database`, i.e. the docker-compose service name — dev/prod behavior unchanged) specifically so tests can point it at `localhost` instead.

## Architecture

Python (FastAPI) + PostgreSQL backend (Postgres not wired up yet — deliberately deferred, see `KANBAN.md` Task 2), React/TypeScript (Vite) frontend, Docker Compose for local dev. LLM calls delegate to existing tooling (Claude Code CLI via subprocess, or OpenRouter) rather than a metered Anthropic API key — no API key config exists yet, this lands with the `/chat` endpoint (Task 3).

## Gotchas (found 2026-08-20 — read before touching Docker/CI here)

- **Kaniko (this repo's actual CI builder) does not support BuildKit `RUN --mount` syntax** — silently ignored, not an error, so `uv`'s own official Docker recipe (`RUN --mount=type=bind,source=uv.lock,...`) fails with a confusing "No pyproject.toml found" instead of a clear "unsupported syntax" error. It builds fine locally (Docker Desktop/Engine defaults to BuildKit) but fails on Jenkins. Keep `backend/Dockerfile` on plain `COPY` — don't reintroduce `--mount` even if a tutorial/AI suggests it.
- **`backend/uv.lock` must be tracked in git** — it was briefly gitignored by a default `uv init`-style `.gitignore` (meant for libraries, not applications), which broke `uv sync --frozen` in CI. If a lockfile-related build failure shows up again, check `git ls-files` includes it before debugging further.
- **Docker Compose volume mounts must target where the app actually imports from, not a generic convention path.** The backend mount is `./backend/core:/code/core` — matches `WORKDIR /code` + `uvicorn core.main:app`. An earlier version mounted to `/code/app` (copied from a generic FastAPI tutorial) — silently broke hot-reload, since nothing ever read that path.
- **Don't add a volume mount to the frontend service.** It runs a built static bundle (`serve -s dist`), not a dev server — mounting host source over `/app` clobbers the built `dist/` and `node_modules` baked into the image, causing 404s. For frontend dev iteration, run `pnpm dev` on the host instead.
- **pnpm global installs don't work in this Docker image** (`pnpm add -g <pkg>` fails — pnpm's global bin dir isn't in `PATH` inside the container, and there's no interactive shell for `pnpm setup` to fix it). Add packages as normal (non-global) dependencies and invoke via `pnpm exec <pkg>`.
- **Root cause chain, traced from the actual git graph + reflog, 2026-08-26 (PR #2)**: the local checkout got left on `main` after a prior sync (a process gap on Claude Code's side, not a user mistake — see "CI/CD" below for the standing fix). A commit landed on `main` by accident as a result. It was cherry-picked onto `dev` to correct it (same content, same author timestamp — confirmed via `git reflog show dev`, which has no trace of any merge, only the cherry-pick). Because `main` still had its own copy of that same change, GitHub's PR page flagged a **merge conflict** on those files when comparing `dev` against `main` — and offered **"Update branch"** as the suggested fix. Clicking it merges `main` into `dev` **directly on GitHub's servers**, with no local git command involved at all (confirmed absent from the local reflog) — producing a "Merge branch 'main' into dev" commit that Gitea's `dev` never sees. The next push from Gitea's `dev` (via the Jenkins "Mirror to GitHub" stage) then fails non-fast-forward — confirmed from the actual build log (`error: failed to push some refs`).
  - **Fix when this happens**: `git fetch github dev`, confirm the old Gitea tip is still an ancestor (`git merge-base --is-ancestor <old-tip> github/dev`) and the file content is actually identical, then `git rebase github/dev` locally and `git push origin dev --force-with-lease`.
  - **Standing fix to prevent it**: always return to `dev` explicitly right after any operation that touches `main` (a PR sync, a direct fix on `main`) — never leave the working tree checked out on `main` between sessions. This is the actual root cause, not the merge/conflict/Update-branch chain that follows from it.
- **`DatabaseClient`'s read methods (`get_history`, `get_exchanges`, `get_details`) never commit or close the transaction SQLAlchemy implicitly opens on a `SELECT`** (found 2026-08-26, writing Task 8's tests). Harmless in the running app (one long-lived connection, never contended), but it means the connection can sit idle-in-transaction holding a lock — surfaced as a real hang in the test suite, where a prior test's `SELECT` blocked the next test's `TRUNCATE` indefinitely. Worked around on the test side (`backend/tests/conftest.py` rolls back `db_client`'s connection before each truncate) rather than changed in `DatabaseClient` itself, since it's not causing a problem in production as currently used — revisit if that ever changes (e.g. multiple concurrent connections, longer-lived idle transactions actually blocking something real).
- **Missing `.dockerignore` + the new `Test:` stages sharing a workspace with `Build & Push:` broke Jenkins build #19** (found 2026-08-26, right after Task 8 shipped). `Test: frontend` runs `pnpm install` in `frontend/` in the Jenkins workspace; `Build & Push: frontend` then uses that same `frontend/` directory as its Kaniko context. With no `.dockerignore`, the Dockerfile's `COPY . .` pulled the Test stage's `node_modules` (pnpm-store-symlinked to a path that doesn't exist inside the Kaniko image) on top of the image's own freshly-installed `node_modules` — tripping pnpm's dependency-consistency check with no TTY to confirm a purge (`ERR_PNPM_ABORTED_REMOVE_MODULES_DIR_NO_TTY`). Fixed by adding `frontend/.dockerignore` (`node_modules`, `dist`, `.git`, `.env*`) and, preemptively, `backend/.dockerignore` (`.venv`, `__pycache__`, same class of risk from `Test: backend`'s `uv sync`, even though it hadn't failed a build yet). Verified locally: a real `docker build` of `frontend/` with local `node_modules`/`dist` already present now succeeds. **General lesson**: any CI pipeline where a test stage and a Docker-build stage share a workspace needs a `.dockerignore` from day one, not just a `.gitignore` — the two are not interchangeable, and this repo had only the latter.

## CI/CD

Gitea (source of truth) → Jenkins multibranch (`Jenkinsfile`): checkout → mirror to GitHub (SSH deploy key, `github-mirror-sovereign-ai-nexus` Jenkins credential, write-scoped to this repo only via a GitHub Deploy Key — not a broader PAT) → Kaniko build **per service** (`backend` and `frontend` are separate stages in the same pipeline, each with its own context/Dockerfile/image tag — not separate Jenkins jobs; one stage failing doesn't block the other) → push to the private registry. The mirror stage runs before the build stages, independent of build success. `main` and `dev` both mirror automatically; no manual promotion step.

Deployment to a running environment (k3s namespaces for staging/prod) isn't wired up yet — deliberately deferred until there's a database and a real endpoint worth deploying, not just this skeleton.

## Git workflow (standing rule, 2026-08-26)

Claude Code owns git mechanics here — branch hygiene, commits, pushes, fetches, rebases, Gitea↔GitHub sync. The one thing that stays the user's own action: clicking "Merge pull request" on GitHub's web UI (kept deliberately, for portfolio/authorship visibility — don't do this yourself even if you technically could via `gh`).

- `dev` is the working branch. **Always verify the current branch before committing** (`git branch --show-current`) — don't assume the working tree is where you left it.
- **Never leave the working tree checked out on `main` between turns/sessions.** This exact mistake (checkout left on `main` after a sync) is what caused a real incident on 2026-08-26 — see the "Update branch" gotcha below for the full chain it triggered.
- Commit incrementally with clear messages as you go, push to `origin` (Gitea) — don't batch everything into one commit at the end, and don't leave work uncommitted for a later session to sort out.
- When a PR eventually gets merged on GitHub, sync it back: `git fetch github main`, verify fast-forward safety (`git merge-base --is-ancestor origin/main github/main`), `git merge --ff-only github/main`, `git push origin main` — then switch back to `dev` immediately.

## Non-goals (v1 — see the private vault note for the full list/reasoning)

No auth/OAuth/JWT, no multi-panel UI, no multi-agent orchestration, no public deploy yet. Conversation history CRUD is **no longer a non-goal** (added 2026-08-26, pulled forward from the deferred list — see KANBAN). Don't add the rest without checking the vault note first — several were deliberately excluded to keep scope small (this project's whole premise is avoiding the scope-creep that killed its two predecessor project ideas).

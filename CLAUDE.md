# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status (updated 2026-08-26)

Tasks 1-5 done: Postgres (global `DatabaseClient`, `lifespan`-managed), `POST /chat` delegating to `claude -p` with real conversation history, and a working chat UI (`react-markdown`+`remark-gfm` rendering, verified via headless browser). Task 6 (Docker Compose end-to-end wiring) is next — see "Known gap" below, there's a real architectural decision to make before starting it, not just wiring. See `KANBAN.md` for a live per-task view (Backlog/In Progress/Done); full task detail (Goal/Visible output/Done when for each task) lives in a private vault note outside this repo — ask if you need that context, don't assume it's summarized correctly here.

### Known gap for Task 6 — CORS / proxy (decide before starting)

The dev-only Vite proxy (`vite.config.ts`, `/chat` → `:8000`) only exists for `pnpm dev`. The Docker frontend is a static build (`serve -s dist`) with no equivalent — a browser hitting `:3000` in the containerized stack gets blocked by the backend's missing CORS headers if it tries `:8000` directly, and `/chat` on `:3000` itself just falls through to the SPA's `index.html` (no proxy layer there at all). Two real options, not yet decided:
- Add `CORSMiddleware` to the FastAPI backend — simplest, but couples frontend/backend origins together unless configured carefully.
- Put a reverse proxy in front of both services so the browser only ever talks to one origin — more setup, but closer to how this would actually get deployed publicly later.

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
- **Root cause chain, traced from the actual git graph + reflog, 2026-08-26 (PR #2)**: the local checkout got left on `main` after a prior sync (a process gap on Claude Code's side, not a user mistake — see "CI/CD" below for the standing fix). A commit landed on `main` by accident as a result. It was cherry-picked onto `dev` to correct it (same content, same author timestamp — confirmed via `git reflog show dev`, which has no trace of any merge, only the cherry-pick). Because `main` still had its own copy of that same change, GitHub's PR page flagged a **merge conflict** on those files when comparing `dev` against `main` — and offered **"Update branch"** as the suggested fix. Clicking it merges `main` into `dev` **directly on GitHub's servers**, with no local git command involved at all (confirmed absent from the local reflog) — producing a "Merge branch 'main' into dev" commit that Gitea's `dev` never sees. The next push from Gitea's `dev` (via the Jenkins "Mirror to GitHub" stage) then fails non-fast-forward — confirmed from the actual build log (`error: failed to push some refs`).
  - **Fix when this happens**: `git fetch github dev`, confirm the old Gitea tip is still an ancestor (`git merge-base --is-ancestor <old-tip> github/dev`) and the file content is actually identical, then `git rebase github/dev` locally and `git push origin dev --force-with-lease`.
  - **Standing fix to prevent it**: always return to `dev` explicitly right after any operation that touches `main` (a PR sync, a direct fix on `main`) — never leave the working tree checked out on `main` between sessions. This is the actual root cause, not the merge/conflict/Update-branch chain that follows from it.

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

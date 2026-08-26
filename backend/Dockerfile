FROM ghcr.io/astral-sh/uv:0.12.5-python3.14-alpine

# Set metadata for the image
LABEL project="SovereignAI Nexis" \
      maintainer="Petrickah <36566884+Petrickah@users.noreply.github.com>" \
      version="1.0" \
      description="Self-hosted AI chat + artifact platform — FastAPI/PostgreSQL backend, React/TypeScript frontend. Backend + AI Platform Engineering portfolio project (planning stage)."

WORKDIR /code

# Claude Code CLI (Task 3 — chat delegation). Installed via npm, not a native
# binary installer: this base image is Alpine (musl libc), and we already hit
# the glibc-vs-musl trap once with a native binary (Hugo, see the blog
# project's CLAUDE.md) — Node.js has an official Alpine build, so npm avoids
# repeating that class of bug. Auth is via CLAUDE_CODE_OAUTH_TOKEN (env var,
# set in docker-compose.yml from .env) — no ~/.claude credentials to mount.
RUN apk add --no-cache nodejs npm && \
    npm install -g @anthropic-ai/claude-code

# Minimal, empty workspace claude -p runs from — this is a text-generation
# call (prompt in, response out), not a coding agent editing real files, so
# no project/repo content belongs here. Revisit only if a future feature
# needs Claude Code to actually operate on real files.
RUN mkdir -p /workspace

# Install dependencies (separate layer, cached while only source changes).
# Plain COPY, not "RUN --mount=type=bind" (uv's own Docker docs use that, but
# it's BuildKit-only syntax — Kaniko, the builder this CI uses, ignores it
# silently instead of erroring, so uv.lock/pyproject.toml never land in the
# image and "uv sync" fails with "No pyproject.toml found". Confirmed
# 2026-08-20 from the actual Kaniko build log — no BuildKit-specific RUN
# --mount syntax in this repo's Dockerfiles, Kaniko doesn't support it).
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# Copy the project into the image
ADD . /code

# Sync the project
RUN uv sync --frozen

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "core.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

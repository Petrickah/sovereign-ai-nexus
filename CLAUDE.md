# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

None yet — no build/lint/test exists. This section fills in once the initial scaffold (Docker Compose, backend, frontend) lands.

## Architecture

Planned: Python (FastAPI) + PostgreSQL backend, React/TypeScript (Vite) frontend, Docker Compose for local dev. LLM calls delegate to existing tooling (Claude Code CLI or OpenRouter) rather than a metered Anthropic API key. Full planning/architecture/task breakdown lives in a private note outside this repository — ask if you need that context.

## CI/CD

Gitea (source of truth) → Jenkins multibranch (`Jenkinsfile`): checkout → mirror to GitHub (SSH deploy key, `github-mirror-sovereign-ai-nexus` Jenkins credential, write-scoped to this repo only via a GitHub Deploy Key — not a broader PAT) → Docker build via Kaniko → push to the private registry. The mirror stage runs independent of the build stage succeeding. `main` and `dev` both mirror; no manual promotion step (unlike the blog project, nothing here needs to stay private).

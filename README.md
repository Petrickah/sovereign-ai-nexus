# Sovereign AI Nexus

## Overview

A small, self-hosted AI chat + artifact web app — a FastAPI/PostgreSQL backend, a React/TypeScript frontend, and an LLM layer that delegates to existing tooling instead of adding new metered API costs. Backend + AI Platform Engineering portfolio project, built incrementally.

## Status

Early scaffold — backend and frontend both run locally with a working dev loop, but there's no database and no chat endpoint yet. Built incrementally, in the open, no fixed timeline.

## Setup

```
docker compose up -d --build
```
Backend on `:8000`, frontend on `:3000`. See `CLAUDE.md` for architecture notes and known gotchas.

## Usage

N/A yet — no functional endpoint until the `/chat` route lands.

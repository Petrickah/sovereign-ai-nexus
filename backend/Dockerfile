FROM ghcr.io/astral-sh/uv:0.12.5-python3.14-alpine

# Set metadata for the image
LABEL project="SovereignAI Nexis" \
      maintainer="Petrickah <36566884+Petrickah@users.noreply.github.com>" \
      version="1.0" \
      description="Self-hosted AI chat + artifact platform — FastAPI/PostgreSQL backend, React/TypeScript frontend. Backend + AI Platform Engineering portfolio project (planning stage)."

WORKDIR /code

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Copy the project into the image
ADD . /code

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "core.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

import os

# Must run before `core.main` is imported anywhere in the test session: the
# module instantiates a global `DatabaseClient()` at import time, which reads
# these env vars once and opens a real connection. Points at the disposable
# Postgres from `docker-compose.test.yml` (repo root), never the dev stack's
# `database` service.
os.environ.setdefault("DATABASE_HOST", "localhost")
os.environ.setdefault("DATABASE_PORT", "5433")
os.environ.setdefault("DATABASE_USER", "test")
os.environ.setdefault("DATABASE_PASSWORD", "test")
os.environ.setdefault("DATABASE_NAME", "test")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from core.main import app, db_client

# A separate connection from the app's own `db_client`, used only to reset
# table state between tests — keeps test cleanup independent of whatever the
# app code under test does with its own connection/transactions.
_cleanup_engine = create_engine(
    "postgresql://{user}:{password}@{host}:{port}/{name}".format(
        user=os.environ["DATABASE_USER"],
        password=os.environ["DATABASE_PASSWORD"],
        host=os.environ["DATABASE_HOST"],
        port=os.environ["DATABASE_PORT"],
        name=os.environ["DATABASE_NAME"],
    )
)


@pytest.fixture(autouse=True)
def clean_exchanges():
    # `db_client`'s read methods (get_history/get_exchanges/get_details)
    # never commit or close the implicit transaction SQLAlchemy opens on
    # SELECT, so a prior test can leave its connection idle-in-transaction,
    # holding a lock that would otherwise block this TRUNCATE indefinitely
    # (confirmed live: this hung for real against the actual test Postgres).
    # Rolling back here is test-teardown hygiene only — not a production fix.
    db_client._connect.rollback()
    with _cleanup_engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE exchanges RESTART IDENTITY"))
    yield


@pytest.fixture(scope="session")
def client():
    # Session-scoped: `db_client` is a module-level singleton, and the app's
    # lifespan closes its connection on shutdown. A per-test TestClient
    # context would trigger that shutdown after the first test, leaving
    # every later test with a dead connection (matches how the real process
    # runs too — started once, alive for many requests).
    with TestClient(app) as c:
        yield c

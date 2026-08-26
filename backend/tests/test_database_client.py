from datetime import datetime, timezone

from core.main import db_client


def test_get_exchanges_returns_distinct_typed_columns():
    # Regression test for the real bug on record (Task 3): a SELECT with
    # parentheses around the column list (`SELECT (id, prompt, ...)`) returns
    # a single Postgres composite/row-type value per row instead of separate
    # columns — `row.id` then either raises or holds a stringified tuple like
    # "(1,hello,hi,2026-01-01...)" instead of the int 1. Asserting real,
    # correctly-typed values here would fail if that ever came back.
    created_at = datetime.now(timezone.utc)
    new_id = db_client.insert_exchange("hello", "hi there", created_at)

    [row] = db_client.get_exchanges(msg_count=10)

    assert row.id == new_id
    assert isinstance(row.id, int)
    assert row.prompt == "hello"
    assert row.response == "hi there"
    assert isinstance(row.prompt, str)
    assert isinstance(row.response, str)


def test_get_exchanges_orders_most_recent_first_and_respects_limit():
    for i in range(5):
        db_client.insert_exchange(f"prompt-{i}", f"response-{i}", datetime.now(timezone.utc))

    rows = db_client.get_exchanges(msg_count=3)

    assert [row.prompt for row in rows] == ["prompt-4", "prompt-3", "prompt-2"]


def test_delete_all_exchanges_returns_the_deleted_count():
    db_client.insert_exchange("a", "a-response", datetime.now(timezone.utc))
    db_client.insert_exchange("b", "b-response", datetime.now(timezone.utc))

    deleted = db_client.delete_all_exchanges()

    assert deleted == 2
    assert db_client.get_history() == []

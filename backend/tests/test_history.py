from datetime import datetime, timedelta, timezone

from core.main import db_client


def _insert(prompt: str, offset_seconds: int) -> int:
    created_at = datetime.now(timezone.utc) + timedelta(seconds=offset_seconds)
    return db_client.insert_exchange(prompt, f"{prompt}-response", created_at)


def test_get_history_returns_exchanges_in_chronological_order(client):
    _insert("third", offset_seconds=20)
    _insert("first", offset_seconds=0)
    _insert("second", offset_seconds=10)

    res = client.get("/history")

    assert res.status_code == 200
    prompts = [item["prompt"] for item in res.json()]
    assert prompts == ["first", "second", "third"]


def test_delete_exchange_removes_only_that_one(client):
    keep_id = _insert("keep me", offset_seconds=0)
    delete_id = _insert("delete me", offset_seconds=1)

    res = client.delete(f"/history/{delete_id}")

    assert res.status_code == 200
    assert res.json() == {"id": delete_id}

    remaining = [item.id for item in db_client.get_history()]
    assert remaining == [keep_id]


def test_delete_unknown_exchange_returns_404(client):
    res = client.delete("/history/999999")

    assert res.status_code == 404


def test_delete_all_history_clears_everything_and_reports_count(client):
    _insert("one", offset_seconds=0)
    _insert("two", offset_seconds=1)
    _insert("three", offset_seconds=2)

    res = client.delete("/history")

    assert res.status_code == 200
    assert res.json() == {"deleted": 3}
    assert db_client.get_history() == []

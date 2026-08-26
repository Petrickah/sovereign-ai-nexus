import asyncio
from datetime import datetime, timezone

from core.main import db_client


async def _fake_call_llm(prompt: str) -> str:
    return f"echo: {prompt}"


def test_chat_persists_exchange_with_mocked_llm(client, monkeypatch):
    monkeypatch.setattr("core.main.call_llm", _fake_call_llm)

    res = client.post("/chat", json={"prompt": "hello"})

    assert res.status_code == 200
    body = res.json()
    assert body["prompt"] == "hello"
    assert body["response"] == "echo: hello"

    history = db_client.get_history()
    assert len(history) == 1
    assert history[0].id == body["id"]
    assert history[0].prompt == "hello"
    assert history[0].response == "echo: hello"


def test_chat_never_invokes_the_real_subprocess(client, monkeypatch):
    # If `call_llm` weren't mocked, this would shell out to the real `claude`
    # CLI and either hang or fail in the test environment — asserting the
    # mock actually replaced it is the guardrail against that.
    calls = []

    async def spy_call_llm(prompt: str) -> str:
        calls.append(prompt)
        return "mocked"

    monkeypatch.setattr("core.main.call_llm", spy_call_llm)
    client.post("/chat", json={"prompt": "ping"})

    assert calls == ["ping"]


def test_created_at_is_captured_before_the_llm_call(client, monkeypatch):
    # Regression test for the real bug on record (Task 3): created_at was
    # originally captured *after* call_llm returned, via Python's kwarg
    # evaluation order. A slow, self-timestamping mock LLM call reproduces
    # the conditions that bug needed to be visible: if created_at were ever
    # captured after the LLM call again, it would land after
    # `llm_started_at + delay`, violating the assertion below.
    llm_started_at = {}

    async def slow_call_llm(prompt: str) -> str:
        llm_started_at["value"] = datetime.now(timezone.utc)
        await asyncio.sleep(0.2)
        return "slow response"

    monkeypatch.setattr("core.main.call_llm", slow_call_llm)

    before_request = datetime.now(timezone.utc)
    res = client.post("/chat", json={"prompt": "hi"})
    after_request = datetime.now(timezone.utc)

    created_at = datetime.fromisoformat(res.json()["created_at"])

    assert before_request <= created_at <= llm_started_at["value"]
    assert created_at < after_request

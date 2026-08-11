from __future__ import annotations

from structlog.contextvars import bind_contextvars, clear_contextvars

from app import agent as agent_module
from tests.test_agent_prompt_trace import RecordingLangfuseClient


def test_trace_metadata_includes_correlation_id_when_present(monkeypatch) -> None:
    clear_contextvars()
    bind_contextvars(correlation_id="req-abc12345")

    client = RecordingLangfuseClient()
    monkeypatch.setattr(agent_module, "get_langfuse_client", lambda: client)

    agent = agent_module.LabAgent()
    agent_module.LabAgent.run.__wrapped__(
        agent,
        user_id="user-01",
        feature="qa",
        session_id="session-01",
        message="Test query",
    )

    trace_metadata = client.trace_updates[-1]["metadata"]
    assert trace_metadata["correlation_id"] == "req-abc12345"
    clear_contextvars()


def test_trace_metadata_defaults_to_missing_when_correlation_id_absent(monkeypatch) -> None:
    clear_contextvars()

    client = RecordingLangfuseClient()
    monkeypatch.setattr(agent_module, "get_langfuse_client", lambda: client)

    agent = agent_module.LabAgent()
    agent_module.LabAgent.run.__wrapped__(
        agent,
        user_id="user-01",
        feature="qa",
        session_id="session-01",
        message="Test query",
    )

    trace_metadata = client.trace_updates[-1]["metadata"]
    assert trace_metadata["correlation_id"] == "MISSING"
    clear_contextvars()

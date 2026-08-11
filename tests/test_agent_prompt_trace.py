from structlog.contextvars import bind_contextvars, clear_contextvars

from app import agent as agent_module


class ManagedPrompt:
    version = 3

    def compile(self, **variables: str) -> str:
        return (
            f"Feature={variables['feature']}\n"
            f"Docs={variables['docs']}\n"
            f"Question={variables['message']}"
        )


class RecordingLangfuseClient:
    def __init__(self) -> None:
        self.prompt = ManagedPrompt()
        self.trace_updates: list[dict] = []
        self.generation_updates: list[dict] = []
        self.span_updates: list[dict] = []

    def get_prompt(self, name: str, **kwargs):
        return self.prompt

    def update_current_trace(self, **kwargs) -> None:
        self.trace_updates.append(kwargs)

    def update_current_generation(self, **kwargs) -> None:
        self.generation_updates.append(kwargs)

    def update_current_span(self, **kwargs) -> None:
        self.span_updates.append(kwargs)


def test_agent_links_prompt_version_to_trace_and_generation(monkeypatch) -> None:
    clear_contextvars()
    bind_contextvars(correlation_id="req-test1234")
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "test-public-key")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("LANGFUSE_PROMPT_NAME", "day13-chat")
    monkeypatch.setenv("LANGFUSE_PROMPT_LABEL", "production")
    client = RecordingLangfuseClient()
    monkeypatch.setattr(agent_module, "get_langfuse_client", lambda: client)

    agent = agent_module.LabAgent()
    agent_module.LabAgent.run.__wrapped__(
        agent,
        user_id="student-01",
        feature="qa",
        session_id="session-01",
        message="Explain traces",
    )

    trace_metadata = client.trace_updates[-1]["metadata"]
    generation_update = client.generation_updates[-1]
    assert trace_metadata == {
        "correlation_id": "req-test1234",
        "prompt_name": "day13-chat",
        "prompt_label": "production",
        "prompt_version": "3",
        "prompt_source": "langfuse",
    }
    assert generation_update["prompt"] is client.prompt
    assert generation_update["metadata"]["prompt_version"] == "3"
    clear_contextvars()


def test_retrieve_context_records_redacted_input_and_rag_state(monkeypatch) -> None:
    client = RecordingLangfuseClient()
    monkeypatch.setattr(agent_module, "get_langfuse_client", lambda: client)
    monkeypatch.setattr(agent_module, "retrieve", lambda _: ["Refund within 7 days"])
    monkeypatch.setitem(agent_module.STATE, "rag_slow", True)

    docs = agent_module.retrieve_context.__wrapped__(
        "Contact student@example.com about refund",
        "refund",
    )

    assert docs == ["Refund within 7 days"]
    assert client.span_updates == [
        {
            "input": {"query_preview": "Contact [REDACTED_EMAIL] about refund"},
            "output": {"document_count": 1},
            "metadata": {"feature": "refund", "incident_rag_slow": True},
        }
    ]
    monkeypatch.setitem(agent_module.STATE, "rag_slow", False)


from app import incidents
from app.mock_llm import FakeLLM


def test_output_token_limit_caps_cost_spike(monkeypatch) -> None:
    monkeypatch.setenv("MAX_OUTPUT_TOKENS", "240")
    monkeypatch.setattr("app.mock_llm.random.randint", lambda *_: 180)
    monkeypatch.setitem(incidents.STATE, "cost_spike", True)

    response = FakeLLM().generate("test prompt")

    assert response.usage.output_tokens == 240
    monkeypatch.setitem(incidents.STATE, "cost_spike", False)


def test_output_token_limit_does_not_expand_normal_response(monkeypatch) -> None:
    monkeypatch.setenv("MAX_OUTPUT_TOKENS", "240")
    monkeypatch.setattr("app.mock_llm.random.randint", lambda *_: 180)
    monkeypatch.setitem(incidents.STATE, "cost_spike", False)

    response = FakeLLM().generate("test prompt")

    assert response.usage.output_tokens == 180

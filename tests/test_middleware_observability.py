from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app import logging_config
from app.main import app


def test_correlation_id_generated_and_headers_returned(monkeypatch, tmp_path: Path) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    with TestClient(app) as client:
        response = client.post(
            "/chat",
            json={
                "user_id": "student-01",
                "session_id": "session-01",
                "feature": "qa",
                "message": "Hello test",
            },
        )

    assert response.status_code == 200
    headers = response.headers
    assert "x-request-id" in headers
    assert headers["x-request-id"].startswith("req-")
    assert "x-response-time-ms" in headers

    events = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    rec_event = next(e for e in events if e["event"] == "request_received")
    assert rec_event["correlation_id"] == headers["x-request-id"]
    assert rec_event["user_id_hash"] is not None
    assert rec_event["session_id"] == "session-01"
    assert rec_event["feature"] == "qa"
    assert rec_event["model"] == "claude-sonnet-4-5"


def test_correlation_id_preserved_from_request_header(monkeypatch, tmp_path: Path) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    with TestClient(app) as client:
        response = client.post(
            "/chat",
            headers={"x-request-id": "custom-cid-12345"},
            json={
                "user_id": "student-02",
                "session_id": "session-02",
                "feature": "summary",
                "message": "Summarize this",
            },
        )

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "custom-cid-12345"
    events = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    rec_event = next(e for e in events if e["event"] == "request_received")
    assert rec_event["correlation_id"] == "custom-cid-12345"


def test_consecutive_requests_do_not_leak_context(monkeypatch, tmp_path: Path) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    with TestClient(app) as client:
        r1 = client.post(
            "/chat",
            json={
                "user_id": "user-A",
                "session_id": "sess-A",
                "feature": "qa",
                "message": "Message A",
            },
        )
        r2 = client.post(
            "/chat",
            json={
                "user_id": "user-B",
                "session_id": "sess-B",
                "feature": "summary",
                "message": "Message B",
            },
        )

    assert r1.headers["x-request-id"] != r2.headers["x-request-id"]
    events = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    rec_events = [e for e in events if e["event"] == "request_received"]
    assert rec_events[0]["session_id"] == "sess-A"
    assert rec_events[1]["session_id"] == "sess-B"

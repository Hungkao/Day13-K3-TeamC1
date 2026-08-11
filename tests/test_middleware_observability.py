from __future__ import annotations

import json
import re
from pathlib import Path

from fastapi.testclient import TestClient

from app import logging_config
from app.main import app


def test_correlation_id_generation_and_headers(monkeypatch, tmp_path: Path) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    with TestClient(app) as client:
        # Test 1: Auto generate req-<8 hex> when header is missing
        res1 = client.post(
            "/chat",
            json={
                "user_id": "user1",
                "session_id": "s1",
                "feature": "qa",
                "message": "hello",
            },
        )
        assert res1.status_code == 200
        cid1 = res1.headers.get("x-request-id")
        assert cid1 is not None
        assert re.match(r"^req-[0-9a-f]{8}$", cid1)
        assert "x-response-time-ms" in res1.headers

        # Test 2: Preserve custom x-request-id header
        res2 = client.post(
            "/chat",
            headers={"x-request-id": "custom-cid-12345"},
            json={
                "user_id": "user2",
                "session_id": "s2",
                "feature": "qa",
                "message": "test header",
            },
        )
        assert res2.status_code == 200
        assert res2.headers.get("x-request-id") == "custom-cid-12345"

        # Test 3: Multiple requests do not leak context
        events = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
        req_events = [e for e in events if e.get("event") == "request_received"]
        assert len(req_events) >= 2
        assert req_events[0]["correlation_id"] == cid1
        assert req_events[1]["correlation_id"] == "custom-cid-12345"

        # Verify Metadata fields required by schema
        first_req = req_events[0]
        assert "user_id_hash" in first_req
        assert "session_id" in first_req
        assert "feature" in first_req
        assert "model" in first_req
        assert "env" in first_req
        assert "ts" in first_req
        assert "level" in first_req
        assert "service" in first_req


def test_generic_exception_handler_returns_correlation_id(monkeypatch, tmp_path: Path) -> None:
    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    with TestClient(app) as client:
        # Patch agent.run to raise an exception
        monkeypatch.setattr("app.main.agent.run", lambda **kwargs: 1 / 0)

        response = client.post(
            "/chat",
            headers={"x-request-id": "error-test-cid"},
            json={
                "user_id": "user1",
                "session_id": "s1",
                "feature": "qa",
                "message": "trigger error",
            },
        )

    assert response.status_code == 500
    assert response.headers.get("x-request-id") == "error-test-cid"
    assert response.json()["detail"] == "ZeroDivisionError"

    events = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    fail_event = next(e for e in events if e.get("event") == "request_failed")
    assert fail_event["correlation_id"] == "error-test-cid"
    assert fail_event["error_type"] == "ZeroDivisionError"

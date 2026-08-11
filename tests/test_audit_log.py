from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app import audit
from app.main import app


def test_incident_changes_are_written_to_separate_audit_log(
    monkeypatch, tmp_path: Path
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setattr(audit, "AUDIT_LOG_PATH", audit_path)

    with TestClient(app) as client:
        assert client.post("/incidents/cost_spike/enable").status_code == 200
        assert client.post("/incidents/cost_spike/disable").status_code == 200

    records = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
    ]
    assert [record["event"] for record in records] == [
        "incident_enabled",
        "incident_disabled",
    ]
    assert all(record["service"] == "audit" for record in records)
    assert all(record["payload"]["incident"] == "cost_spike" for record in records)

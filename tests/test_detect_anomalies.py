from scripts.detect_anomalies import analyze_logs


def test_detects_latency_and_pii_anomalies() -> None:
    records = [
        {"event": "request_received", "payload": {"message": "a@example.com"}},
        {"event": "response_sent", "latency_ms": 3500, "cost_usd": 0.1},
    ]

    result = analyze_logs(records, latency_threshold_ms=3000)

    assert result["anomaly_count"] == 2
    assert [item["type"] for item in result["anomalies"]] == [
        "latency_p95",
        "pii",
    ]


def test_clean_logs_have_no_anomalies() -> None:
    records = [
        {"event": "request_received"},
        {
            "event": "response_sent",
            "latency_ms": 200,
            "cost_usd": 0.01,
            "quality_score": 0.9,
        },
    ]

    assert analyze_logs(records)["anomaly_count"] == 0

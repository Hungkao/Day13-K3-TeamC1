from dashboard.app import compute_dashboard_metrics


def test_error_rate_does_not_double_count_failed_requests() -> None:
    records = [
        {"event": "request_received"},
        {"event": "request_received"},
        {"event": "response_sent", "latency_ms": 100},
        {"event": "request_failed", "error_type": "RuntimeError"},
    ]

    metrics = compute_dashboard_metrics(records)

    assert metrics["traffic"]["request_received_count"] == 2
    assert metrics["traffic"]["request_failed_count"] == 1
    assert metrics["errors"]["error_rate_pct"] == 50.0
    assert metrics["errors"]["error_breakdown"] == {"RuntimeError": 1}


def test_error_rate_is_zero_without_requests() -> None:
    metrics = compute_dashboard_metrics([])

    assert metrics["errors"]["error_rate_pct"] == 0.0

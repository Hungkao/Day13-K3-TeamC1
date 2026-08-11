import app.metrics as metrics_mod
from app.metrics import percentile, record_error, record_request, snapshot


def reset_metrics() -> None:
    metrics_mod.TRAFFIC = 0
    metrics_mod.REQUEST_LATENCIES.clear()
    metrics_mod.REQUEST_COSTS.clear()
    metrics_mod.REQUEST_TOKENS_IN.clear()
    metrics_mod.REQUEST_TOKENS_OUT.clear()
    metrics_mod.ERRORS.clear()
    metrics_mod.QUALITY_SCORES.clear()


def test_percentile_basic() -> None:
    assert percentile([100, 200, 300, 400], 50) >= 100
    assert percentile([], 95) == 0.0


def test_snapshot_zero_requests() -> None:
    reset_metrics()
    snap = snapshot()
    assert snap["traffic"] == 0
    assert snap["error_rate_pct"] == 0.0
    assert snap["avg_cost_usd"] == 0.0
    assert snap["total_cost_usd"] == 0.0
    assert snap["tokens_in_total"] == 0
    assert snap["tokens_out_total"] == 0
    assert snap["quality_avg"] == 0.0
    assert snap["error_breakdown"] == {}


def test_snapshot_only_success() -> None:
    reset_metrics()
    record_request(latency_ms=150, cost_usd=0.002, tokens_in=10, tokens_out=20, quality_score=0.9)
    record_request(latency_ms=250, cost_usd=0.003, tokens_in=15, tokens_out=25, quality_score=0.85)

    snap = snapshot()
    assert snap["traffic"] == 2
    assert snap["error_rate_pct"] == 0.0
    assert snap["avg_cost_usd"] == 0.0025
    assert snap["total_cost_usd"] == 0.005
    assert snap["tokens_in_total"] == 25
    assert snap["tokens_out_total"] == 45
    assert snap["quality_avg"] == 0.875


def test_snapshot_only_errors() -> None:
    reset_metrics()
    record_error("rate_limit")
    record_error("rate_limit")

    snap = snapshot()
    assert snap["traffic"] == 0
    assert snap["error_rate_pct"] == 100.0
    assert snap["error_breakdown"] == {"rate_limit": 2}


def test_snapshot_mixed_requests() -> None:
    reset_metrics()
    record_request(latency_ms=100, cost_usd=0.01, tokens_in=50, tokens_out=50, quality_score=0.8)
    record_request(latency_ms=200, cost_usd=0.01, tokens_in=50, tokens_out=50, quality_score=0.9)
    record_error("llm_timeout")
    record_error("rag_failure")

    snap = snapshot()
    assert snap["traffic"] == 2
    # 2 errors out of 4 total requests (2 traffic + 2 errors) -> 50%
    assert snap["error_rate_pct"] == 50.0
    assert snap["error_breakdown"] == {"llm_timeout": 1, "rag_failure": 1}


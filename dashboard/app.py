from __future__ import annotations

import json
import sys
from pathlib import Path
from statistics import mean

REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_FILE = REPO_ROOT / "data" / "logs.jsonl"


def percentile(values: list[float | int], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[idx])


def load_logs(file_path: Path) -> list[dict]:
    if not file_path.exists():
        return []
    records = []
    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records


def compute_dashboard_metrics(records: list[dict]) -> dict:
    req_received = [r for r in records if r.get("event") == "request_received"]
    resp_sent = [r for r in records if r.get("event") == "response_sent"]
    req_failed = [r for r in records if r.get("event") == "request_failed"]

    latencies = [r["latency_ms"] for r in resp_sent if "latency_ms" in r]
    costs = [r["cost_usd"] for r in resp_sent if "cost_usd" in r]
    tokens_in = [r["tokens_in"] for r in resp_sent if "tokens_in" in r]
    tokens_out = [r["tokens_out"] for r in resp_sent if "tokens_out" in r]
    quality_scores = [r["quality_score"] for r in resp_sent if "quality_score" in r]

    errors_count = len(req_failed)
    total_requests = len(req_received) + errors_count
    error_rate = (errors_count / total_requests * 100) if total_requests > 0 else 0.0

    error_breakdown = {}
    for r in req_failed:
        err_type = r.get("error_type", "unknown")
        error_breakdown[err_type] = error_breakdown.get(err_type, 0) + 1

    return {
        "time_range": "60m",
        "total_records": len(records),
        "traffic": {
            "request_received_count": len(req_received),
            "response_sent_count": len(resp_sent),
            "request_failed_count": len(req_failed),
        },
        "latency": {
            "p50": percentile(latencies, 50),
            "p95": percentile(latencies, 95),
            "p99": percentile(latencies, 99),
            "threshold_p95_lte": 3000,
            "status_p95": "OK" if percentile(latencies, 95) <= 3000 else "VIOLATED",
        },
        "errors": {
            "error_rate_pct": round(error_rate, 2),
            "error_breakdown": error_breakdown,
            "threshold_lte": 2.0,
            "status": "OK" if error_rate <= 2.0 else "VIOLATED",
        },
        "cost": {
            "total_cost_usd": round(sum(costs), 4),
            "avg_cost_usd": round(mean(costs), 4) if costs else 0.0,
            "threshold_lte": 2.5,
            "status": "OK" if sum(costs) <= 2.5 else "VIOLATED",
        },
        "tokens": {
            "tokens_in_total": sum(tokens_in),
            "tokens_out_total": sum(tokens_out),
            "tokens_sum": sum(tokens_in) + sum(tokens_out),
            "threshold_lte": 50000,
            "status": "OK" if (sum(tokens_in) + sum(tokens_out)) <= 50000 else "VIOLATED",
        },
        "quality": {
            "quality_avg": round(mean(quality_scores), 4) if quality_scores else 0.0,
            "threshold_gte": 0.75,
            "status": "OK" if (mean(quality_scores) if quality_scores else 0.0) >= 0.75 else "VIOLATED",
        },
    }


def render_terminal_dashboard(metrics: dict) -> None:
    print("=" * 60)
    print("           DAY 13 AI OBSERVABILITY DASHBOARD           ")
    print("=" * 60)
    print(f"Time Window : Last 60 Minutes | Refresh: 30s")
    print(f"Total Logs  : {metrics['total_records']} lines\n")

    print("[Panel 1: Latency Percentiles]")
    print(f"  P50: {metrics['latency']['p50']:.1f} ms | P95: {metrics['latency']['p95']:.1f} ms | P99: {metrics['latency']['p99']:.1f} ms")
    print(f"  Threshold (P95 <= 3000 ms): [{metrics['latency']['status_p95']}]\n")

    print("[Panel 2: Request Traffic]")
    print(f"  Requests Received : {metrics['traffic']['request_received_count']}")
    print(f"  Responses Sent    : {metrics['traffic']['response_sent_count']}")
    print(f"  Requests Failed   : {metrics['traffic']['request_failed_count']}\n")

    print("[Panel 3: Error Rate & Breakdown]")
    print(f"  Error Rate : {metrics['errors']['error_rate_pct']}%")
    print(f"  Breakdown  : {json.dumps(metrics['errors']['error_breakdown'])}")
    print(f"  Threshold (Error Rate <= 2.0%): [{metrics['errors']['status']}]\n")

    print("[Panel 4: Cost Over Time]")
    print(f"  Total Cost : ${metrics['cost']['total_cost_usd']:.4f} USD")
    print(f"  Threshold (Total Cost <= $2.50 USD): [{metrics['cost']['status']}]\n")

    print("[Panel 5: Input & Output Tokens]")
    print(f"  Tokens In  : {metrics['tokens']['tokens_in_total']}")
    print(f"  Tokens Out : {metrics['tokens']['tokens_out_total']}")
    print(f"  Threshold (Total Tokens <= 50,000): [{metrics['tokens']['status']}]\n")

    print("[Panel 6: Quality Proxy]")
    print(f"  Mean Score : {metrics['quality']['quality_avg']:.4f}")
    print(f"  Threshold (Quality Avg >= 0.75): [{metrics['quality']['status']}]")
    print("=" * 60)


def main() -> None:
    file_path = Path(sys.argv[1]) if len(sys.argv) > 1 else LOG_FILE
    records = load_logs(file_path)
    metrics = compute_dashboard_metrics(records)
    render_terminal_dashboard(metrics)


if __name__ == "__main__":
    main()

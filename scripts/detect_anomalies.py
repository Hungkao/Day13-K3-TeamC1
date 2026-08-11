from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.pii import PII_PATTERNS
from dashboard.app import compute_dashboard_metrics, load_logs


def analyze_logs(
    records: list[dict],
    *,
    latency_threshold_ms: float = 3000,
    error_rate_threshold_pct: float = 2.0,
    cost_threshold_usd: float = 2.5,
) -> dict:
    metrics = compute_dashboard_metrics(records)
    pii_hits = []
    for record in records:
        rendered = json.dumps(record, ensure_ascii=False)
        detected = sorted(
            name
            for name, pattern in PII_PATTERNS.items()
            if re.search(pattern, rendered)
        )
        if detected:
            pii_hits.append({"event": record.get("event"), "types": detected})

    anomalies = []
    if metrics["latency"]["p95"] > latency_threshold_ms:
        anomalies.append(
            {
                "type": "latency_p95",
                "value": metrics["latency"]["p95"],
                "threshold": latency_threshold_ms,
            }
        )
    if metrics["errors"]["error_rate_pct"] > error_rate_threshold_pct:
        anomalies.append(
            {
                "type": "error_rate_pct",
                "value": metrics["errors"]["error_rate_pct"],
                "threshold": error_rate_threshold_pct,
            }
        )
    if metrics["cost"]["total_cost_usd"] > cost_threshold_usd:
        anomalies.append(
            {
                "type": "total_cost_usd",
                "value": metrics["cost"]["total_cost_usd"],
                "threshold": cost_threshold_usd,
            }
        )
    if pii_hits:
        anomalies.append({"type": "pii", "hits": pii_hits})

    return {
        "records": len(records),
        "anomaly_count": len(anomalies),
        "anomalies": anomalies,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect observability anomalies from JSONL logs")
    parser.add_argument("log_path", nargs="?", default="data/logs.jsonl")
    parser.add_argument("--latency-threshold-ms", type=float, default=3000)
    parser.add_argument("--error-rate-threshold-pct", type=float, default=2.0)
    parser.add_argument("--cost-threshold-usd", type=float, default=2.5)
    args = parser.parse_args()

    result = analyze_logs(
        load_logs(Path(args.log_path)),
        latency_threshold_ms=args.latency_threshold_ms,
        error_rate_threshold_pct=args.error_rate_threshold_pct,
        cost_threshold_usd=args.cost_threshold_usd,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if result["anomaly_count"] else 0)


if __name__ == "__main__":
    main()

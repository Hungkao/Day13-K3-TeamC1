# Technical acceptance — 2026-08-11

## Final verification

```text
python -m pytest -q
42 passed, 2 warnings

python scripts/validate_logs.py
Total log records analyzed: 15
Missing required fields: 0
Missing enrichment: 0
Potential PII leaks: 0
Estimated Score: 100/100

python scripts/validate_dashboard.py
HỢP LỆ: 6/6 panel có trong dashboard contract.

git diff --check
exit code 0
```

Hai warning là FastAPI `on_event` deprecation, không phải test failure.

## Challenge acceptance

- Baseline P95: `198 ms`.
- Challenge P95: `2707 ms`, vượt ngưỡng `2000 ms`.
- Trace: `8ffc1862d57f573a234a59f49eab5da2`.
- Correlation ID: `req-feed1303`.
- Observation `retrieve-context`: `2.501 s`, metadata `incident_rag_slow=true`.
- `/health`: `ok=true`, tracing bật, tất cả incident đã tắt sau nghiệm thu.

## Prompt acceptance

- `day13-chat` v1: labels `baseline`, `production`.
- `day13-chat` v2: label `candidate`.
- Baseline trace: `c7af89d1fde84429c458ca092dd97d47`.
- Candidate trace: `3824f432373f555607e5450e008b149d`.
- Tổng trace trong project khi nghiệm thu: `35`.

## Bonus acceptance

- Cost optimization: `$0.0778` → `$0.0370`, giảm `52.4%`; quality giữ `0.88`.
- Audit log riêng: `submission/evidence/bonus/audit-log.jsonl`.
- Custom automation: detector phát hiện challenge P95 `2707 > 2000 ms` và trả exit code 1.

## Safety

- `.env`, `.venv/`, `data/logs.jsonl`, `data/audit.jsonl` được Git ignore.
- Evidence JSONL parse hợp lệ.
- PII evidence chỉ chứa marker `[REDACTED_*]`, không chứa giá trị PII đầu vào.
- Quét exact Langfuse key được thực hiện trước commit; không có key trong file dự kiến nộp.

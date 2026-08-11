# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: Team C1
- Repository URL: `https://github.com/Hungkao/Day13-K3-TeamC1`
- Commit SHA cuối: `2e8ca15aad2f385964a6f3499b72f7314375edb1`
- Thành viên và vai trò:
  - Nguyễn Phúc Hưng — MSSV `2A202601115`: Metrics, dashboard 6 panel, SLO, alert rules và runbook.
  - Nguyễn Văn Phong — MSSV `2A202601087`: Structured logging, correlation ID và PII redaction.
  - Nguyễn Hữu Khánh Tùng — MSSV `2A202601781`: Langfuse tracing, prompt versioning và rollback evidence.
  - Nguyễn Tuấn Vũ — MSSV `2A202601845`: Lead tích hợp, challenge investigation, kiểm thử, bonus và báo cáo cuối.

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: `100/100`.
- Tổng số traces: `35` traces trong project Langfuse tại thời điểm nghiệm thu.
- Số PII leak còn lại: `0`.
- Link/đường dẫn dashboard: `dashboard/app.py`; evidence `submission/evidence/dashboard/dashboard-runtime.png`.

## 3. Logging và tracing

- Evidence correlation ID: `submission/evidence/incident/retriever-trace-log.jsonl`, correlation ID `req-feed1303` liên kết log với trace `8ffc1862d57f573a234a59f49eab5da2`.
- Evidence PII redaction: `submission/evidence/logging/pii-redaction-evidence.jsonl`; email, điện thoại, thẻ, CCCD, passport và địa chỉ đều được thay bằng `[REDACTED_*]`.
- Evidence trace waterfall: `submission/evidence/tracing/trace-waterfall.png`.
- Giải thích một span đáng chú ý: observation `retrieve-context` trong trace `8ffc1862d57f573a234a59f49eab5da2` kéo dài `2.501 s`, nằm dưới generation `run` `4.060 s`, có metadata `feature=refund` và `incident_rag_slow=true`; đây là bước chiếm phần lớn latency và chỉ đúng bottleneck retrieval.

## 4. Prompt versioning

- Prompt name: `day13-chat`.
- Version/label baseline: v1, labels `baseline` và `production`.
- Version/label candidate: v2, label `candidate`.
- Trace ID của mỗi version: baseline `c7af89d1fde84429c458ca092dd97d47`; candidate `3824f432373f555607e5450e008b149d`; chi tiết tại `submission/evidence/tracing/prompt-version-trace-ids.md`.
- Bằng chứng đổi label hoặc rollback: `submission/evidence/tracing/prompt-rollback-evidence.png`; bằng chứng hai version tại `submission/evidence/tracing/prompt-versions-traces.png`.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel có trong dashboard contract`.
- Evidence dashboard: `submission/evidence/dashboard/dashboard-runtime.png`.
- SLO đã chọn và lý do: P95 latency `<= 3000 ms`, error rate `<= 2%`, rolling cost `<= $2.50`, quality trung bình `>= 0.75`; các ngưỡng cân bằng trải nghiệm, độ ổn định, chi phí và chất lượng. Challenge dùng ngưỡng operational riêng `2000 ms` để phát hiện sớm.
- Alert rules và runbook: `config/alert_rules.yaml` và `docs/alerts.md`.

## 6. Điều tra challenge

- Challenge ID: `day13-k3-observability-v1`.
- Triệu chứng từ metrics: baseline P95 `198 ms`; challenge P95 `2707 ms`, tăng `2509 ms` (`1267.2%`), vượt ngưỡng challenge `2000 ms`; error rate vẫn `0%`, quality vẫn `0.86`.
- Trace ID liên quan: `8ffc1862d57f573a234a59f49eab5da2`; observation `retrieve-context` `2.501 s`.
- Log line/correlation ID liên quan: `req-feed1303`, `response_sent.latency_ms=4058`; file `submission/evidence/incident/retriever-trace-log.jsonl`.
- Root cause: khi `rag_slow=true`, `app/mock_rag.py` gọi blocking `time.sleep(2.5)` trong đường xử lý endpoint async, làm chậm retrieval và chặn event loop.
- Fix action: chuyển retrieval sang async hoặc thread pool, đặt timeout và fallback; mitigation trong lab là tắt incident và xác nhận `/health` trả tất cả incident `false`.
- Preventive measure: observation `retrieve-context`, anomaly detector theo P95, alert theo feature, concurrency regression, timeout/circuit-breaker metrics. Phân tích đầy đủ tại `submission/evidence/incident/incident-analysis.md`.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Nguyễn Phúc Hưng (`2A202601115`) | Metrics, dashboard, SLO, alert rules và runbook | [9bdbd10](https://github.com/Hungkao/Day13-K3-TeamC1/commit/9bdbd10) | Cách chuyển log thành SLI/SLO và alert dựa trên triệu chứng. |
| Nguyễn Văn Phong (`2A202601087`) | JSON logging, correlation ID, metadata và PII redaction | [860ef78](https://github.com/Hungkao/Day13-K3-TeamC1/commit/860ef78), [2f0e945](https://github.com/Hungkao/Day13-K3-TeamC1/commit/2f0e945) | Cách nối request bằng correlation ID và scrub PII trước khi ghi log. |
| Nguyễn Hữu Khánh Tùng (`2A202601781`) | Langfuse tracing, prompt v1/v2 và rollback evidence | [fac1c26](https://github.com/Hungkao/Day13-K3-TeamC1/commit/fac1c26), [4aa6de3](https://github.com/Hungkao/Day13-K3-TeamC1/commit/4aa6de3) | Cách liên kết prompt version, trace metadata và session/correlation ID. |
| Nguyễn Tuấn Vũ (`2A202601845`) | Lead tích hợp, load-test safety, challenge, retriever span, bonus, kiểm thử và báo cáo | [53b8605](https://github.com/Hungkao/Day13-K3-TeamC1/commit/53b8605), [2e8ca15](https://github.com/Hungkao/Day13-K3-TeamC1/commit/2e8ca15) | Cách điều tra Metrics → Traces → Logs, kiểm soát cost, audit incident và nghiệm thu evidence trung thực. |

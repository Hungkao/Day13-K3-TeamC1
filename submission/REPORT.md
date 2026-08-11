# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: Team C1
- Repository URL: [Điền URL repository]
- Commit SHA cuối: [Điền Commit SHA cuối]
- Thành viên và vai trò:
  - Phong: HTTP Logging, Correlation ID & PII Redaction
  - Tùng: Langfuse Tracing & Prompt Versioning
  - Hưng: Metrics, Dashboard, SLO & Alert Rules / Runbook
  - Vũ (Lead): Challenge Tooling, Validators, Integration & Báo cáo tổng hợp

## 2. Kết quả kỹ thuật

*(Lưu ý: Dữ liệu thực tế sẽ do Vũ tổng hợp từ kết quả chạy thực nghiệm và handoff của các thành viên)*

- Điểm `validate_logs.py`: [Chưa chạy / Điền điểm thực tế sau tích hợp]
- Tổng số traces: [Điền số lượng trace thực tế thu thập được]
- Số PII leak còn lại: [Điền số lượng PII leak thực tế]
- Link/đường dẫn dashboard: [Điền link hoặc file dashboard tương ứng]

## 3. Logging và tracing

*(Do Phong & Tùng cung cấp dữ liệu qua handoff, bằng chứng lưu tại `submission/evidence/logging/` và `submission/evidence/tracing/`)*

- Evidence correlation ID: `submission/evidence/logging/correlation-id.png` (hoặc log snippet)
- Evidence PII redaction: `submission/evidence/logging/pii-redacted.png` (hoặc log snippet)
- Evidence trace waterfall: `submission/evidence/tracing/trace-waterfall.png`
- Giải thích một span đáng chú ý: [Phân tích span từ Langfuse trace]

## 4. Prompt versioning

*(Do Tùng cung cấp dữ liệu qua handoff, bằng chứng lưu tại `submission/evidence/tracing/`)*

- Prompt name: `day13-chat`
- Version/label baseline: [v1 / baseline / production]
- Version/label candidate: [v2 / candidate]
- Trace ID của mỗi version:
  - Baseline Trace ID: [Điền Trace ID thật]
  - Candidate Trace ID: [Điền Trace ID thật]
- Bằng chứng đổi label hoặc rollback: `submission/evidence/tracing/prompt-rollback.png`

## 5. Dashboard, SLO và alerts

*(Do Hưng cung cấp dữ liệu qua handoff, bằng chứng lưu tại `submission/evidence/dashboard/`)*

- Kết quả `validate_dashboard.py`: [Chưa chạy / Điền kết quả thực tế 6/6 panel]
- Evidence dashboard: `submission/evidence/dashboard/dashboard-runtime.png`
- SLO đã chọn và lý do: [Mô tả SLO P95 latency, Error rate, Quality score...]
- Alert rules và runbook: [Dẫn tới `config/alert_rules.yaml` và `docs/alerts.md`]

## 6. Điều tra challenge

*(Do Vũ trực tiếp thực thi và thu thập bằng chứng tại `submission/evidence/incident/`)*

- Challenge ID: `day13-k3-observability-v1`
- Triệu chứng từ metrics: [Ghi nhận triệu chứng Latency P95 / Error Rate từ Dashboard]
- Trace ID liên quan: [Điền Trace ID thực tế của challenge]
- Log line/correlation ID liên quan: [Điền Correlation ID và log line thực tế]
- Root cause: [Phân tích nguyên nhân gốc rễ sau khi chạy challenge]
- Fix action: [Biện pháp khắc phục sự cố]
- Preventive measure: [Biện pháp phòng ngừa lâu dài]

## 7. Đóng góp cá nhân

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Phong | Logging, Correlation ID & PII Redaction | [PR/Commit Link] | [Nội dung đã học] |
| Tùng | Langfuse Tracing & Prompt Versioning | [PR/Commit Link] | [Nội dung đã học] |
| Hưng | Metrics, Dashboard, SLO & Alert Rules | [PR/Commit Link] | [Nội dung đã học] |
| Vũ (Lead) | Challenge Tooling, Integration & Report | [PR/Commit Link] | [Nội dung đã học] |

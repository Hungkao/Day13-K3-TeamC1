# Đặc tả chung — Lab 13 AI Observability

Tài liệu này là thỏa thuận kỹ thuật chung để nhóm Hưng, Phong, Vũ và Tùng triển khai song song. Mọi thành viên và coding agent phải đọc file này trước khi sửa code.

## 1. Mục tiêu và phạm vi

Hoàn thiện một hệ thống AI có thể quan sát và điều tra theo chuỗi:

```text
Metrics -> Traces -> Logs -> Root cause -> Fix -> Preventive measure
```

Kết quả cuối phải có:

- Structured JSON logging, correlation ID và PII redaction.
- Metrics latency, traffic, error, token, cost và quality proxy.
- Ít nhất 10 Langfuse traces có metadata.
- Prompt `day13-chat` có version 1/version 2, label và bằng chứng rollback.
- Dashboard runtime đúng 6 panel, SLO, alert và runbook.
- Điều tra challenge K3 bằng metric, trace ID và log/correlation ID cụ thể.
- Báo cáo, evidence, test và Git history có thể kiểm chứng.

Không tối ưu ngoài phạm vi trước khi toàn bộ yêu cầu bắt buộc đạt Definition of Done.

## 2. Thứ tự ưu tiên nguồn yêu cầu

Khi tài liệu có vẻ khác nhau, áp dụng thứ tự sau:

1. `RULES.md`: giới hạn an toàn và tính trung thực.
2. `RUBRIC.md` và `SUBMISSION.md`: tiêu chí chấm và nội dung nộp.
3. `README.md` và `CHECKPOINTS.md`: luồng làm bài và checkpoint.
4. Contract máy đọc trong `config/` và hành vi validator.
5. Hướng dẫn chi tiết trong `docs/`.
6. `team_execution/Lab_13_Observability_Metrics_Traces_Logs.md`: hướng dẫn bổ sung chi tiết cho CP1.

Không dùng public tests như nguồn yêu cầu duy nhất. Test pass không thay thế trace, dashboard runtime, screenshot hoặc evidence.

## 3. Quy tắc làm việc song song

- Mỗi file chỉ có đúng một owner trong giai đoạn song song; ownership nằm trong `todo.md`.
- Chỉ sửa file thuộc danh sách **được tác động** của mình.
- Muốn sửa file ngoài ownership phải báo Vũ và chờ điều phối; không tự sửa “tiện tay”.
- Không format hàng loạt hoặc đổi tên file ngoài phạm vi.
- Không sửa `config/challenge.json` trong mọi trường hợp.
- Không commit `.env`, secret, API key, `.venv/`, cache, log có PII hoặc evidence giả.
- Mỗi người lưu evidence vào thư mục con riêng trong `submission/evidence/` để tránh đụng nhau.
- Mỗi người ghi handoff vào file riêng trong `team_execution/handoffs/`; không cùng sửa một handoff.
- Mỗi thay đổi phải có test/validator phù hợp hoặc giải thích rõ vì sao chưa thể chạy.
- Không hard-code output để vượt validator và không xóa log lỗi nhằm che kết quả.

## 4. Contract logging và PII

### 4.1 Correlation ID

- Đầu mỗi request phải gọi `clear_contextvars()`.
- Ưu tiên header `x-request-id`; nếu thiếu thì sinh `req-<8 ký tự hex>`.
- Bind `correlation_id` vào structlog context.
- Gán vào `request.state.correlation_id`.
- Response thành công phải có `x-request-id` và `x-response-time-ms`.
- Nếu triển khai handler lỗi 500, không được làm mất log `request_failed` hoặc thay đổi contract response ngoài phần được tài liệu cho phép.

### 4.2 Log schema

Mọi record phải tuân theo `config/logging_schema.json`. Các trường bắt buộc toàn cục:

- `ts`, `level`, `service`, `event`, `correlation_id`.

Log `request_received` phải có:

- `user_id_hash`, `session_id`, `feature`, `model`, `env`.

Log `response_sent` phải cung cấp dữ liệu dashboard:

- `latency_ms`, `tokens_in`, `tokens_out`, `cost_usd`, `quality_score`.

Log lỗi phải có `event=request_failed` và `error_type`.

### 4.3 PII

- Không log raw `user_id`; chỉ log hash SHA-256 rút gọn theo code hiện tại.
- Phải che ít nhất email, điện thoại Việt Nam, CCCD, thẻ tín dụng, passport và dấu hiệu địa chỉ Việt Nam theo hướng dẫn lab.
- Scrub phải chạy trước `JsonlFileProcessor` và `JSONRenderer`.
- Scrub mọi string có khả năng đi vào log, kể cả string trong dictionary; không chỉ scrub `payload.message_preview`.
- Không đưa raw prompt/message chứa PII vào trace metadata hoặc log.

## 5. Contract metrics

Snapshot `/metrics` phải có:

- `traffic`.
- `latency_p50`, `latency_p95`, `latency_p99`.
- `avg_cost_usd`, `total_cost_usd`.
- `tokens_in_total`, `tokens_out_total`.
- `error_rate_pct`, `error_breakdown`.
- `quality_avg`.

Theo hướng dẫn lab:

```text
total_errors = sum(ERRORS.values())
total_requests = TRAFFIC + total_errors
error_rate_pct = total_errors / total_requests * 100
```

Trường hợp không có request phải trả `0.0`, không chia cho 0.

## 6. Contract tracing và prompt

- Trace phải liên kết được với log bằng `metadata.correlation_id`.
- Trace giữ `user_id` ở dạng hash, `session_id`, tags cho lab/feature/model.
- Trace và generation phải có `prompt_name`, `prompt_label`, `prompt_version`, `prompt_source`.
- Prompt managed có tên mặc định `day13-chat` và giữ đúng biến:

```text
Feature={{feature}}
Docs={{docs}}
Question={{message}}
```

- Version 1: labels `baseline`, `production`.
- Version 2: label `candidate`.
- Cùng một input phải được chạy với `baseline` và `candidate`.
- Phải có thao tác chuyển `production` sang v2 rồi rollback về v1.
- Khi Langfuse lỗi, app dùng local fallback và ghi đúng `local`/`local-fallback`; tuyệt đối không giả version managed.

## 7. Contract dashboard, SLO và alert

Nguồn chuẩn của dashboard là `data/logs.jsonl`, không phải Langfuse. `config/dashboard.yaml` phải có đúng 6 panel:

1. Latency P50/P95/P99 từ `response_sent.latency_ms`.
2. Traffic từ count `request_received`.
3. Error rate và breakdown từ `request_received`, `request_failed`, `error_type`.
4. Cost từ `response_sent.cost_usd`.
5. Token input/output từ `response_sent.tokens_in/tokens_out`.
6. Quality mean từ `response_sent.quality_score`.

Giữ contract hiện hành:

- Time range: 60 phút.
- Refresh: 30 giây.
- P95 latency: `<= 3000 ms`.
- Error rate: `<= 2%`.
- Total cost: `<= 2.5 USD` trong cửa sổ dashboard.
- Quality mean: `>= 0.75`.

Alert phải dựa trên triệu chứng/SLO, có severity, condition, duration, ảnh hưởng, ba bước kiểm tra đầu, mitigation và owner. Validator chỉ chứng minh YAML hợp lệ; screenshot dashboard runtime vẫn bắt buộc.

## 8. Challenge chính thức

`config/challenge.json` đã được release trong commit `cd84f4f` và là read-only:

- Challenge ID: `day13-k3-observability-v1`.
- Incident: `rag_slow`.
- Feature bị ảnh hưởng: `refund`.
- Ngưỡng challenge: `2000 ms`.

Luồng chạy chính thức:

```powershell
python scripts/inject_incident.py
python scripts/load_test.py --challenge --concurrency 5
```

Kết luận incident chỉ hợp lệ khi có đủ:

- Triệu chứng từ metric/dashboard.
- Trace ID và span bất thường.
- Log line/correlation ID cùng request.
- Root cause phù hợp với cả ba lớp.
- Fix action và preventive measure.

## 9. Evidence và báo cáo

Mỗi ảnh phải rõ tên màn hình, time range/đơn vị nếu là dashboard và không lộ secret. Quy ước thư mục:

```text
submission/evidence/logging/   # Phong
submission/evidence/tracing/   # Tùng
submission/evidence/dashboard/ # Hưng
submission/evidence/incident/  # Vũ
```

Tên file dùng chữ thường, số và dấu gạch ngang, ví dụ `trace-candidate-v2.png`. Tất cả evidence phải được dẫn bằng đường dẫn tương đối trong `submission/REPORT.md`.

Evidence bắt buộc:

- Kết quả cuối `validate_logs.py`.
- Danh sách tối thiểu 10 traces và một trace waterfall.
- Hai prompt version, hai trace gắn đúng version/label và ảnh rollback.
- Log có correlation ID/metadata và PII đã redact.
- Kết quả dashboard validator và dashboard runtime đủ 6 panel.
- Alert rules và runbook.
- Metric, trace ID và log line của challenge.

## 10. Lệnh kiểm tra chuẩn

Sau khi cài dependencies và kích hoạt virtual environment:

```powershell
python -m pytest -q
python scripts/validate_dashboard.py
python scripts/validate_logs.py
git status --short
```

Với kiểm tra runtime:

```powershell
uvicorn app.main:app --reload --env-file .env
python scripts/load_test.py --concurrency 5
```

Không kết luận validator pass nếu lệnh không thực sự chạy do thiếu package hoặc thiếu `data/logs.jsonl`.

## 11. Definition of Done

Bài chỉ hoàn thành khi đồng thời thỏa mãn:

- Không còn TODO bắt buộc trong `app/` và `config/`.
- `/health` hoạt động; load test tạo log hợp lệ.
- `validate_logs.py >= 80/100` và pytest pass hoàn toàn.
- Dashboard validator báo `HỢP LỆ: 6/6 panel`.
- Dashboard runtime đúng dữ liệu và có screenshot.
- Có ít nhất 10 trace thật; prompt version/label/rollback có evidence.
- Challenge được chứng minh theo Metrics -> Traces -> Logs.
- `submission/REPORT.md` đầy đủ, link evidence hợp lệ.
- Git không chứa secret/PII và đóng góp cá nhân khớp commit/PR.

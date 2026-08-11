# TODO phân công song song — Lab 13

Mục tiêu của kế hoạch này là bốn người bắt đầu cùng lúc, hoàn thành deliverable riêng mà không cần chờ code của nhau. File ownership không giao nhau; bước ghép và chạy nghiệm thu toàn hệ thống do Vũ thực hiện sau khi nhận bốn handoff, không làm cản trở việc hoàn thành nhánh cá nhân.

## 0. Quy tắc chung cho mọi người và agent

Trước khi làm, đọc đầy đủ:

1. `team_execution/spec.md`.
2. `RULES.md`, `README.md`, `CHECKPOINTS.md`, `RUBRIC.md`, `SUBMISSION.md`.
3. Tài liệu/file chuyên môn được ghi trong từng nhiệm vụ.

Mỗi người:

- Làm trên branch riêng, commit nhỏ và mô tả đúng nội dung.
- Chỉ sửa file trong mục **Được tác động**.
- Không sửa `config/challenge.json`, `.env`, file của người khác hoặc evidence của người khác.
- Nếu phát hiện vấn đề ngoài ownership: ghi vào handoff, không tự sửa.
- Agent phải trả ra: file đã sửa, lý do, test đã chạy và kết quả, việc chưa thể kiểm tra, rủi ro còn lại, đường dẫn evidence/handoff.
- Nếu dependency chưa được cài, vẫn hoàn thành code/test tĩnh; ghi rõ lệnh cần Vũ chạy lúc tích hợp.

---

## 1. Phong — Logging, correlation ID và PII

### Việc phải làm

Hoàn thiện toàn bộ CP1 thuộc lớp HTTP/logging/PII, không đụng tracing, metrics hay dashboard.

### Được tác động

- `app/middleware.py`
- `app/main.py`
- `app/logging_config.py`
- `app/pii.py`
- `tests/test_chat_observability.py`
- `tests/test_pii.py`
- Có thể tạo mới:
  - `tests/test_middleware_observability.py`
  - `tests/test_logging_context.py`
  - `submission/evidence/logging/*`
  - `team_execution/handoffs/phong.md`

### Không được tác động

- `app/agent.py`, `app/tracing.py`, `app/prompt_management.py`
- `app/metrics.py`
- Toàn bộ `config/`
- `scripts/`
- `submission/REPORT.md`
- `config/challenge.json`
- File/evidence/handoff của thành viên khác

### Các bước chi tiết

1. Đọc `team_execution/Lab_13_Observability_Metrics_Traces_Logs.md`, `docs/GUIDE.md`, `config/logging_schema.json` và `scripts/validate_logs.py`.
2. Trong middleware:
   - Clear contextvars đầu request.
   - Dùng `x-request-id` nếu có; nếu không sinh `req-<8 hex>`.
   - Bind correlation ID và gán request state.
   - Thêm response header `x-request-id`, `x-response-time-ms`.
3. Trong endpoint chat, bind `user_id_hash`, `session_id`, `feature`, `model`, `env` trước `request_received`.
4. Bật `scrub_event` đúng thứ tự processor.
5. Mở rộng scrub để che string ở các field/dictionary; bảo đảm scrub trước khi ghi file/console.
6. Bổ sung regex passport và dấu hiệu địa chỉ Việt Nam, giữ các pattern hiện tại hoạt động.
7. Nếu thêm generic handler cho lỗi 500, phải có test chứng minh correlation ID vẫn được trả và `request_failed` vẫn được log. Đây là phần mở rộng, không được làm hỏng contract hiện tại.
8. Bổ sung test cho:
   - Correlation ID sinh mới đúng format.
   - Correlation ID từ header được giữ nguyên.
   - Request liên tiếp không leak context.
   - Metadata có đủ trường.
   - Email, phone, CCCD, card, passport và địa chỉ được redact.
9. Chạy các test thuộc ownership và ghi kết quả vào handoff.
10. Khi có môi trường runtime, tạo evidence validator và log đã redact trong thư mục riêng.

### Kết quả đầu ra cần đạt

- Không còn `MISSING` cho request hợp lệ.
- Log `request_received` đủ metadata và tuân schema.
- Không có PII mẫu xuất hiện nguyên văn trong log.
- Response có correlation/time headers.
- Test mới/hiện có của phần logging pass.
- `team_execution/handoffs/phong.md` mô tả thay đổi và lệnh kiểm tra.

### Prompt copy cho coding agent của Phong

```text
Bạn phụ trách duy nhất track Logging/Correlation ID/PII của Lab 13.

Đọc đầy đủ theo thứ tự:
1) team_execution/spec.md
2) team_execution/todo.md, mục “Phong”
3) RULES.md, README.md, CHECKPOINTS.md
4) team_execution/Lab_13_Observability_Metrics_Traces_Logs.md
5) docs/GUIDE.md, config/logging_schema.json, scripts/validate_logs.py
6) các file app/middleware.py, app/main.py, app/logging_config.py, app/pii.py và test được phép sửa.

Thực hiện đúng từng bước trong mục Phong. Chỉ sửa các file được liệt kê ở “Được tác động”; không sửa file khác dù thấy lỗi. Bổ sung test có ý nghĩa, không hard-code để qua validator, không tạo hoặc ghi secret/PII thật. Giữ thay đổi tối thiểu và tương thích code hiện tại.

Khi xong, tạo team_execution/handoffs/phong.md và trả ra:
- danh sách file đã sửa;
- hành vi đã hoàn thành;
- test/lệnh đã chạy và output tóm tắt;
- việc chưa thể chạy do môi trường;
- rủi ro hoặc lỗi ngoài ownership;
- đường dẫn evidence nếu có.
```

---

## 2. Tùng — Langfuse tracing và prompt versioning

### Việc phải làm

Hoàn thiện liên kết trace-log, bảo toàn metadata prompt và thực hiện quy trình prompt version/label/rollback trên Langfuse.

### Được tác động

- `app/agent.py`
- `app/tracing.py`
- `app/prompt_management.py`
- `tests/test_agent_prompt_trace.py`
- `tests/test_prompt_management.py`
- `tests/test_tracing_adapter.py`
- Có thể tạo mới:
  - `tests/test_trace_correlation.py`
  - `submission/evidence/tracing/*`
  - `team_execution/handoffs/tung.md`

### Không được tác động

- `app/main.py`, `app/middleware.py`, `app/logging_config.py`, `app/pii.py`
- `app/metrics.py`
- Toàn bộ `config/` và `scripts/`
- `submission/REPORT.md`
- `config/challenge.json`
- File/evidence/handoff của thành viên khác

### Các bước chi tiết

1. Đọc `docs/PROMPT_VERSIONING.md`, `docs/GUIDE.md`, `SETUP.md` và các test tracing/prompt hiện có.
2. Lấy correlation ID hiện hành từ structlog contextvars trong `LabAgent.run`.
3. Thêm correlation ID vào trace metadata, đồng thời giữ nguyên metadata prompt hiện có.
4. Bảo đảm trace có hashed user ID, session, tags và prompt metadata.
5. Bảo đảm generation có model, usage, cost, prompt link và metadata; không capture raw input/output chứa PII ngoài contract.
6. Giữ local fallback minh bạch: `local` hoặc `local-fallback`, không báo giả là managed prompt.
7. Cập nhật test đang so sánh metadata exact để bao gồm correlation ID và bổ sung test khi context thiếu ID.
8. Trên Langfuse:
   - Tạo prompt `day13-chat` đúng ba biến.
   - Tạo v1 với `baseline` và `production`.
   - Tạo v2 với `candidate`.
   - Chạy cùng input cho `baseline` và `candidate`.
   - Chuyển `production` sang v2, chạy một request, rollback về v1.
9. Thu thập tối thiểu 10 trace thật, hai trace ID prompt, trace waterfall và ảnh rollback vào thư mục evidence riêng.
10. Không ghi key vào code, ảnh hoặc handoff.

### Kết quả đầu ra cần đạt

- Trace metadata liên kết được với log qua correlation ID.
- Trace/generation ghi đúng prompt name/label/version/source.
- Test tracing/prompt pass.
- Có tối thiểu 10 traces và đầy đủ evidence prompt/rollback nếu có Langfuse credentials.
- `team_execution/handoffs/tung.md` ghi trace IDs, nhãn/version và đường dẫn evidence nhưng không chứa secret.

### Prompt copy cho coding agent của Tùng

```text
Bạn phụ trách duy nhất track Langfuse Tracing và Prompt Versioning của Lab 13.

Đọc đầy đủ theo thứ tự:
1) team_execution/spec.md
2) team_execution/todo.md, mục “Tùng”
3) RULES.md, README.md, CHECKPOINTS.md, SETUP.md
4) docs/PROMPT_VERSIONING.md và docs/GUIDE.md
5) app/agent.py, app/tracing.py, app/prompt_management.py
6) tests/test_agent_prompt_trace.py, tests/test_prompt_management.py, tests/test_tracing_adapter.py.

Thực hiện đúng mục Tùng. Chỉ sửa file được phép. Thêm correlation_id từ structlog context vào trace metadata mà không làm mất prompt metadata. Giữ fallback trung thực và không log/capture raw PII. Cập nhật test exact metadata tương ứng. Nếu không có Langfuse key, hoàn thành code/test local và cung cấp checklist/lệnh thao tác UI; tuyệt đối không giả trace hoặc version.

Khi xong, tạo team_execution/handoffs/tung.md và trả ra:
- file đã sửa;
- contract trace/prompt đã đạt;
- test đã chạy và kết quả;
- trace IDs/evidence thật nếu có;
- việc bị giới hạn bởi credentials;
- rủi ro ngoài ownership.
```

---

## 3. Hưng — Metrics, dashboard, SLO, alerts và runbook

### Việc phải làm

Hoàn thiện metrics error rate, xác nhận contract dashboard, dựng dashboard runtime, chốt SLO và ba alert/runbook.

### Được tác động

- `app/metrics.py`
- `config/dashboard.yaml`
- `config/slo.yaml`
- `config/alert_rules.yaml`
- `docs/alerts.md`
- `docs/dashboard-spec.md`
- `scripts/validate_dashboard.py`
- `tests/test_metrics.py`
- `tests/test_dashboard_validator.py`
- Có thể tạo mới:
  - `dashboard/*`
  - `tests/test_metrics_snapshot.py`
  - `submission/evidence/dashboard/*`
  - `team_execution/handoffs/hung.md`

### Không được tác động

- `app/main.py`, `app/middleware.py`, `app/logging_config.py`, `app/pii.py`
- `app/agent.py`, `app/tracing.py`, `app/prompt_management.py`
- `app/challenge.py`, `app/incidents.py`, `app/mock_rag.py`, `app/mock_llm.py`
- `scripts/load_test.py`, `scripts/inject_incident.py`, `scripts/validate_logs.py`
- `submission/REPORT.md`
- `config/challenge.json`
- File/evidence/handoff của thành viên khác

### Các bước chi tiết

1. Đọc `docs/DASHBOARD_SETUP.md`, `docs/dashboard-spec.md`, `docs/alerts.md`, `docs/blueprint-template.md`, `config/dashboard.yaml`, `config/slo.yaml` và validator.
2. Thêm `error_rate_pct` vào `metrics.snapshot()` theo công thức trong `spec.md`; bổ sung test cho zero request, chỉ success, chỉ error và hỗn hợp.
3. Không đổi sáu panel hoặc threshold hiện có nếu không có lỗi contract cụ thể.
4. Chạy dashboard validator; nếu sửa validator, phải giữ khả năng từ chối panel thiếu threshold/query và bổ sung test.
5. Dựng dashboard runtime từ `data/logs.jsonl` bằng công cụ phù hợp. Nếu tạo code trong repo, đặt toàn bộ dưới `dashboard/`.
6. Dashboard phải hiển thị đúng 6 panel, time range 60 phút, refresh 30 giây, đơn vị và threshold.
7. Chốt nội dung `config/slo.yaml`, bỏ ghi chú placeholder và giải thích lựa chọn trong handoff.
8. Thay toàn bộ TODO trong `config/alert_rules.yaml` bằng ba alert symptom/SLO-based. Mỗi alert cần condition/duration/severity/owner/runbook rõ ràng.
9. Điền `docs/alerts.md` với ảnh hưởng người dùng, ba bước kiểm tra, mitigation và owner tương ứng.
10. Khi có runtime log, chạy baseline và incident practice `rag_slow`, xác nhận P95 tăng, lưu ảnh validator/dashboard vào thư mục evidence riêng.

### Kết quả đầu ra cần đạt

- `/metrics` có error rate đúng và không chia cho 0.
- Dashboard validator báo `HỢP LỆ: 6/6 panel`.
- Dashboard runtime đủ sáu panel và nhìn rõ threshold/time range/unit.
- Không còn TODO trong alert rules/runbook; SLO và alert nhất quán.
- Test metrics/dashboard pass.
- `team_execution/handoffs/hung.md` ghi cách chạy dashboard, test và đường dẫn evidence.

### Prompt copy cho coding agent của Hưng

```text
Bạn phụ trách duy nhất track Metrics, Dashboard, SLO, Alerts và Runbook của Lab 13.

Đọc đầy đủ theo thứ tự:
1) team_execution/spec.md
2) team_execution/todo.md, mục “Hưng”
3) RULES.md, README.md, CHECKPOINTS.md, RUBRIC.md
4) docs/DASHBOARD_SETUP.md, docs/dashboard-spec.md, docs/alerts.md, docs/blueprint-template.md
5) config/dashboard.yaml, config/slo.yaml, config/alert_rules.yaml
6) app/metrics.py, scripts/validate_dashboard.py và test được phép sửa.

Làm đúng mục Hưng và chỉ sửa file được phép. Trước hết triển khai error_rate_pct và test biên. Giữ dashboard contract đúng sáu panel từ data/logs.jsonl; không hard-code số liệu. Hoàn thiện SLO, ba alert symptom-based và runbook nhất quán. Nếu tạo dashboard code, đặt trong dashboard/. Nếu chưa có logs runtime, dùng fixture/test để hoàn thành code nhưng ghi rõ rằng screenshot thật còn cần chạy sau; không làm giả evidence.

Khi xong, tạo team_execution/handoffs/hung.md và trả ra:
- file đã sửa;
- công thức/contract đã áp dụng;
- cách chạy dashboard;
- test/validator và kết quả;
- evidence thật nếu có;
- phần runtime chưa thể xác nhận;
- rủi ro ngoài ownership.
```

---

## 4. Vũ (Lead) — Challenge, kiểm chứng tích hợp, report và nộp bài

### Việc phải làm

Sở hữu tooling challenge và toàn bộ bước nghiệm thu/tích hợp. Trong lúc ba thành viên khác làm code, Vũ có thể kiểm tra challenge, chuẩn hóa report/evidence và chuẩn bị kịch bản demo mà không sửa file của họ.

### Được tác động

- `app/challenge.py`
- `app/incidents.py`
- `app/mock_rag.py`
- `app/mock_llm.py`
- `scripts/load_test.py`
- `scripts/inject_incident.py`
- `scripts/validate_logs.py`
- `tests/test_challenge_config.py`
- `tests/test_cli_windows_encoding.py`
- `tests/test_validate_logs.py`
- `submission/REPORT.md`
- `submission/evidence/incident/*`
- `team_execution/handoffs/vu.md`
- Sau khi nhận handoff: quyền merge/integrate và chỉ sửa ngoài ownership để giải quyết conflict hoặc lỗi tích hợp đã được ghi nhận.

### Không được tác động trong giai đoạn song song

- Các file đang thuộc ownership của Phong, Tùng và Hưng.
- `config/challenge.json` — luôn luôn read-only, kể cả lúc tích hợp.
- Evidence/handoff của thành viên khác.
- `.env`, secret hoặc dữ liệu PII.

### Các bước chi tiết

1. Đọc toàn bộ tài liệu cấp cao, `app/challenge.py`, incident implementations, load/inject scripts và challenge tests.
2. Xác nhận `config/challenge.json` là file tracked từ commit release và ghi SHA vào handoff; không sửa nội dung.
3. Kiểm tra loader từ chối challenge sai, giữ thứ tự query deterministic và practice scenario vẫn chạy không cần release file.
4. Kiểm tra `load_test.py --challenge --concurrency 5` dùng query chính thức và in correlation ID an toàn.
5. Kiểm tra `validate_logs.py` phát hiện PII raw và không báo pass giả khi file thiếu/rỗng/sai JSON.
6. Chuẩn hóa `submission/REPORT.md` theo toàn bộ mục bắt buộc, tạo chỗ dẫn evidence riêng cho từng owner; chưa điền dữ liệu giả.
7. Chuẩn bị kịch bản demo: health -> baseline -> dashboard symptom -> trace span -> log correlation -> root cause -> fix/prevention -> prompt rollback.
8. Sau khi nhận bốn handoff/commit:
   - Merge các track theo thứ tự bất kỳ vì ownership không giao nhau.
   - Cài dependencies, chạy full pytest và validator.
   - Chạy API/load test để tạo log sạch.
   - Chạy challenge chính thức, thu metric/trace/log evidence thật.
   - Điền report bằng ID, số liệu và đường dẫn thật.
   - Kiểm tra secret/PII/Git status và commit SHA cuối.
9. Nếu tích hợp lỗi, ưu tiên sửa tại owner file tương ứng và ghi lý do trong commit; không nới validator hoặc xóa evidence lỗi.

### Kết quả đầu ra cần đạt

- Challenge tooling/test hoạt động và `config/challenge.json` nguyên vẹn.
- Report có cấu trúc đầy đủ, sau tích hợp chứa toàn bộ evidence thật.
- Full pytest pass, log validator đạt ít nhất 80/100 và dashboard validator 6/6.
- Có kết luận challenge theo Metrics -> Traces -> Logs cùng fix/prevention.
- Git sạch secret/PII; repo URL và final SHA sẵn sàng nộp.
- `team_execution/handoffs/vu.md` là biên bản nghiệm thu cuối.

### Prompt copy cho coding agent của Vũ

```text
Bạn hỗ trợ Vũ, lead tích hợp của Lab 13. Bạn phụ trách duy nhất Challenge tooling, validation, report và nghiệm thu cuối.

Đọc đầy đủ theo thứ tự:
1) team_execution/spec.md
2) toàn bộ team_execution/todo.md, đặc biệt mục “Vũ (Lead)” và ownership của ba người còn lại
3) RULES.md, README.md, CHECKPOINTS.md, RUBRIC.md, SUBMISSION.md
4) config/challenge.json ở chế độ chỉ đọc
5) app/challenge.py, app/incidents.py, app/mock_rag.py, app/mock_llm.py
6) scripts/load_test.py, scripts/inject_incident.py, scripts/validate_logs.py
7) test và submission/REPORT.md được phép sửa.

Trong giai đoạn song song, tuyệt đối không sửa file thuộc Phong/Tùng/Hưng và không sửa config/challenge.json. Kiểm tra tooling challenge/validator, bổ sung test hợp lệ và chuẩn hóa report mà không điền evidence giả. Sau khi các handoff đã có, thực hiện full integration: chạy test/validator/runtime, điều tra challenge bằng metric -> trace -> log, điền report bằng dữ liệu thật và kiểm tra secret/PII.

Khi xong, tạo team_execution/handoffs/vu.md và trả ra:
- commit/handoff đã nhận;
- file đã sửa;
- toàn bộ lệnh nghiệm thu và kết quả;
- metric, trace ID, correlation ID/log evidence thật;
- root cause, fix và preventive measure;
- repo/final SHA hoặc việc còn chặn nộp bài.
```

---

## 5. Ma trận ownership nhanh

| Phạm vi | Owner | Evidence | Handoff |
|---|---|---|---|
| HTTP logging, correlation, PII | Phong | `submission/evidence/logging/` | `handoffs/phong.md` |
| Langfuse trace, prompt version/rollback | Tùng | `submission/evidence/tracing/` | `handoffs/tung.md` |
| Metrics, dashboard, SLO, alert/runbook | Hưng | `submission/evidence/dashboard/` | `handoffs/hung.md` |
| Challenge, validators, report, integration | Vũ | `submission/evidence/incident/` | `handoffs/vu.md` |

Không có file source/config/test nào được giao cho hai người cùng lúc. Các phụ thuộc runtime chỉ xuất hiện ở nghiệm thu cuối do lead thực hiện; chúng không ngăn mỗi thành viên hoàn thành code, test và handoff của track mình.

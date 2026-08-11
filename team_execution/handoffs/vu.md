# Biên bản handoff — Giai đoạn 1 của Vũ (Lead Integration)

- Người thực hiện: Vũ
- Ngày nghiệm thu: 2026-08-11
- Phạm vi: Challenge tooling, load-test safety và khung báo cáo tích hợp
- Trạng thái: **HOÀN THÀNH GIAI ĐOẠN 1**
- Git commit/push: **Chưa thực hiện**

Trạng thái trên chỉ áp dụng cho phạm vi Giai đoạn 1 được ghi trong tài liệu này. Full test suite, API runtime, dashboard, Langfuse traces và điều tra challenge chính thức thuộc bước tích hợp sau khi nhận handoff của các thành viên còn lại.

## 1. File đã tác động

Đúng ba file thuộc ownership của Vũ:

- `[MODIFY]` `scripts/load_test.py`
- `[MODIFY]` `submission/REPORT.md`
- `[NEW]` `team_execution/handoffs/vu.md`

Kết quả `git status --short --untracked-files=all` khi nghiệm thu:

```text
 M scripts/load_test.py
 M submission/REPORT.md
?? team_execution/handoffs/vu.md
```

Không sửa `config/challenge.json` và không có file thuộc ownership của Phong, Tùng hoặc Hưng trong working-tree diff.

## 2. Thay đổi đã thực hiện

### `scripts/load_test.py`

`send_request()` lấy correlation ID theo thứ tự:

1. Header `x-request-id`.
2. Field `correlation_id` nếu response body parse được thành JSON object.
3. Chuỗi `"None"` nếu cả hai nguồn trên không có.

JSON body chỉ được parse khi header không cung cấp correlation ID. Lỗi parse JSON được xử lý để response HTTP 500 hoặc non-JSON không làm load test crash. Format output được giữ nguyên:

```text
[status_code] correlation_id | feature | latency_ms
```

Đã loại bỏ khoảng trắng thừa; `git diff --check` không còn cảnh báo lỗi định dạng.

### `submission/REPORT.md`

- Bổ sung cấu trúc chi tiết cho các mục bắt buộc.
- Phân vai bốn thành viên.
- Phân định evidence bằng đường dẫn tương đối:
  - Phong: `submission/evidence/logging/`
  - Tùng: `submission/evidence/tracing/`
  - Hưng: `submission/evidence/dashboard/`
  - Vũ: `submission/evidence/incident/`
- Chỉ sử dụng placeholder cho kết quả chưa chạy; không điền trace ID, validator result hoặc evidence giả.

## 3. Kiểm tra tĩnh challenge và tooling

### `config/challenge.json` — chỉ đọc

- Cohort: `K3`
- Challenge ID: `day13-k3-observability-v1`
- Incident: `rag_slow`
- Feature bị ảnh hưởng: `refund`
- Latency threshold: `2000 ms`
- Số query chính thức: 5

File không xuất hiện trong Git diff.

### Tooling liên quan

- `app/challenge.py` validate release config và giữ query order deterministic theo seed.
- Practice incident có thể được chọn độc lập với release config.
- `scripts/validate_logs.py` kiểm tra required fields, enrichment và PII; file log thiếu/rỗng/sai JSON không được báo pass.

Các nhận định trong mục này dựa trên đọc code và các targeted tests bên dưới; chưa phải kết quả chạy challenge runtime.

## 4. Kết quả kiểm thử đã chạy

### Regression trực tiếp cho `send_request()`

Chạy bằng `.venv\Scripts\python.exe` với fake HTTP client/response trong bộ nhớ, không tạo file test ngoài ownership:

| Ca kiểm tra | Kỳ vọng | Kết quả |
|---|---|---|
| HTTP 500 có `x-request-id`; JSON parser cố tình báo lỗi nếu bị gọi | Dùng header, không parse JSON | PASS |
| HTTP 200 không có header, JSON object có `correlation_id` | Dùng ID từ JSON | PASS |
| HTTP 500 không có header, body non-JSON | In `None`, không crash | PASS |
| HTTP 500 không có header, JSON là list | In `None`, không crash | PASS |

Kết quả: **4/4 ca pass**.

### Targeted ownership tests

Lệnh:

```powershell
.\.venv\Scripts\python.exe -m pytest `
  tests/test_challenge_config.py `
  tests/test_cli_windows_encoding.py `
  tests/test_validate_logs.py -q
```

Kết quả:

```text
........                                                                 [100%]
8 passed in 1.09s
```

### CLI compatibility

Lệnh:

```powershell
.\.venv\Scripts\python.exe scripts/load_test.py --help
```

Kết quả: exit code 0; các option `--concurrency` và `--challenge` vẫn tồn tại, không lỗi encoding.

### Diff validation

`git diff --check` trả exit code 0.

### Kiểm tra tích hợp sau khi nhận code Hưng và Phong

Sau khi merge hai nhánh thành viên vào `main`, tạo `feature/vu` và khôi phục phần việc Giai đoạn 1 của Vũ:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/validate_dashboard.py
```

Kết quả:

```text
32 passed, 2 warnings in 5.34s
HỢP LỆ: 6/6 panel có trong dashboard contract.
```

Hai warning là cảnh báo deprecation của FastAPI `on_event`, không phải test failure. Regression trực tiếp của `send_request()` tiếp tục đạt 4/4 ca sau khi code Phong và Hưng đã được merge.

## 5. Chưa thực hiện sau kiểm tra tích hợp tĩnh

Các nội dung sau không được báo là pass và sẽ do Vũ nghiệm thu ở bước tích hợp:

- Chạy API và load test với server thật.
- `validate_logs.py` trên `data/logs.jsonl` runtime.
- Dashboard runtime với dữ liệu thật và screenshot.
- Langfuse traces, prompt labels/version và rollback.
- Challenge chính thức theo chuỗi Metrics -> Traces -> Logs.
- Điền số liệu, trace ID, correlation ID và evidence thật vào report.

## 6. Kết luận handoff

Giai đoạn 1 của Vũ đã hoàn thành trong đúng ownership: fallback correlation ID được triển khai và kiểm tra trực tiếp, report có khung tích hợp nhưng không chứa dữ liệu giả, challenge config được giữ nguyên, targeted tests và full test suite sau merge đều pass, dashboard contract hợp lệ và diff sạch.

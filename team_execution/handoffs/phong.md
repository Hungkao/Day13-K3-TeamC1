# Handoff Track 1: Phong — Logging, Correlation ID và PII

## 1. Danh sách file đã sửa / tạo mới
- `app/middleware.py`: Triển khai `CorrelationIdMiddleware` với `clear_contextvars()`, trích xuất/sinh `x-request-id` theo format `req-<8 hex>`, bind contextvars, gán `request.state.correlation_id`, và trả headers `x-request-id`, `x-response-time-ms`.
- `app/main.py`: Thêm `bind_contextvars` enrich context (`user_id_hash`, `session_id`, `feature`, `model`, `env`) trước log `request_received` trong endpoint `/chat`. Thêm `generic_exception_handler` để giữ `x-request-id` header khi có 500 error.
- `app/logging_config.py`: Mở rộng `scrub_event` để lọc PII đệ quy cho tất cả chuỗi thuộc tính dict/string trong event dict và đăng ký `scrub_event` processor trước `JsonlFileProcessor`/`JSONRenderer`.
- `app/pii.py`: Bổ sung regex patterns cho `passport` và `address_vn`.
- `tests/test_pii.py`: Thêm test case kiểm tra redact CCCD, Credit Card, Passport, và Địa chỉ VN.
- `tests/test_middleware_observability.py` (Mới): Thêm test case kiểm tra correlation ID sinh mới, correlation ID từ header request, và cách ly contextvars giữa các request liên tiếp.

## 2. Kết quả kiểm tra
- **pytest**: Pass 26/26 tests (`.\.venv\Scripts\pytest`).
- **validate_logs.py**: Đạt **100/100** điểm.
  - Basic JSON schema: PASSED
  - Correlation ID propagation: PASSED (10 unique correlation IDs)
  - Log enrichment: PASSED
  - PII scrubbing: PASSED (0 leaks detected)

## 3. Hướng dẫn nghiệm thu cho Vũ (Lead)
- Chạy lệnh test: `.\.venv\Scripts\pytest`
- Chạy load test sinh log: `.\.venv\Scripts\python scripts/load_test.py`
- Kiểm tra log validator: `.\.venv\Scripts\python scripts/validate_logs.py`

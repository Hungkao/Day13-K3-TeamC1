# Runbook và Quy trình Xử lý Alert (Alerting & Runbook Specification)

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

---

## Alert 1: HighLatencyP95

- **Tên**: `HighLatencyP95`
- **Severity**: `Critical`
- **SLI/SLO liên quan**: `latency_p95_ms <= 3000ms` (Target 99.5%)
- **Điều kiện và thời gian duy trì**: P95 latency vượt quá `3000 ms` liên tục trong `2 phút`.
- **Ảnh hưởng tới người dùng**: Người dùng gặp phản hồi chậm vượt mức chấp nhận được, có thể xảy ra timeout ở phía UI hoặc client app.
- **Ba bước kiểm tra đầu tiên**:
  1. **Kiểm tra Dashboard Metrics**: Xác định xu hướng P50 vs P95/P99 trên panel `Latency percentiles` xem latency tăng đột biến trên toàn hệ thống hay chỉ riêng 1 endpoint/feature (vd: `refund`).
  2. **Khoanh vùng bằng Trace**: Mở Langfuse dashboard, lọc các traces có latency > 3000ms. Phân tích Waterfall span xem thời gian tiêu tốn nhiều nhất ở bước nào (Mock RAG retrieval hay LLM generation).
  3. **Đối chiếu Log bằng Correlation ID**: Lấy `correlation_id` từ trace chậm, tra cứu trong `data/logs.jsonl` để kiểm tra log `request_received` / `response_sent` nhằm xem thông số `feature`, `model` và thông điệp lỗi nếu có.
- **Mitigation tạm thời**:
  - Nếu sự cố do RAG service chậm (như scenario `rag_slow`), kích hoạt fallback bypass cache hoặc tắt tạm thời retrieval cho feature bị ảnh hưởng.
  - Tăng timeout hoặc chuyển hướng traffic sang model/fallback node dự phòng.
- **Owner**: Hung (Metrics & Alerting)

---

## Alert 2: HighErrorRate

- **Tên**: `HighErrorRate`
- **Severity**: `Critical`
- **SLI/SLO liên quan**: `error_rate_pct <= 2%` (Target 99.0%)
- **Điều kiện và thời gian duy trì**: Tỷ lệ lỗi (`error_rate_pct`) vượt quá `2%` liên tục trong `3 phút`.
- **Ảnh hưởng tới người dùng**: Câu trả lời của AI bị ngắt quãng, trả về lỗi hệ thống hoặc không phản hồi.
- **Ba bước kiểm tra đầu tiên**:
  1. **Kiểm tra Panel Errors**: Kiểm tra panel `Error rate and breakdown` trên Dashboard để xem loại lỗi chính đang xảy ra (`error_type` như `rate_limit`, `llm_timeout`, `rag_failure`, `internal_error`).
  2. **Kiểm tra Health Endpoint**: Gọi thử `/health` và `/metrics` của app để xác nhận ứng dụng còn sống hay đang quá tải.
  3. **Truy vết Log lỗi**: Tìm các log record có `event == "request_failed"` trong `data/logs.jsonl` và lọc theo `error_type` để đọc chi tiết ngoại lệ và `correlation_id`.
- **Mitigation tạm thời**:
  - Nếu gặp `rate_limit` từ upstream LLM, bật tính năng backoff/retry tự động hoặc hạ tốc độ request (rate limiting tại gateway).
  - Tạm thời thông báo maintenance cho feature bị lỗi nặng nếu là sự cố ngoài tầm kiểm soát upstream.
- **Owner**: Hung (Metrics & Alerting)

---

## Alert 3: HighCostBurnRate

- **Tên**: `HighCostBurnRate`
- **Severity**: `Warning`
- **SLI/SLO liên quan**: `daily_cost_usd <= $2.5 USD` (Target 100% trong cửa sổ 60 phút)
- **Điều kiện và thời gian duy trì**: Tổng chi phí (`total_cost_usd`) vượt quá `$2.5 USD` trong cửa sổ rolling 60 phút.
- **Ảnh hưởng tới người dùng**: Không ảnh hưởng trực tiếp đến UX nhưng vượt ngân sách dự toán hệ thống (vượt threshold chi phí).
- **Ba bước kiểm tra đầu tiên**:
  1. **Kiểm tra Panel Cost & Tokens**: Xem panel `Cost over time` và `Input and output tokens` để biết token tăng đột biến ở chiều Input hay Output.
  2. **Soi Trace tiêu tốn Token**: Lọc danh sách traces có `cost_usd` hoặc `tokens_out` cao bất thường trong Langfuse.
  3. **Kiểm tra Log & Feature**: Lọc log theo `response_sent` có `tokens_out > 2000` để phát hiện prompt lặp lại hoặc vắng mặt max_tokens limit.
- **Mitigation tạm thời**:
  - Áp dụng cấu hình siết chặt `max_tokens` cho câu trả lời LLM.
  - Tạm thời áp dụng prompt ngắn hơn hoặc bật cache câu trả lời trùng lặp.
- **Owner**: Hung (Metrics & Alerting)


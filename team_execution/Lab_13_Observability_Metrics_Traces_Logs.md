# Lab 13 — Observability cho hệ thống AI: Metrics, Traces & Logs

**Tập trung**

**Ghi chú0**

**Hỗ trợ**

**Tiếng Việt**

[**2**](https://codelabs.vlearn.dev/profile "26ai.vunt2@vinuni.edu.vn")

**Quay lạiTiếp**

## 3. Block 1 — Structured Logging, Correlation ID & PII (Checkpoint CP1)

**⏱ Thời gian: 60 phút · Bắt đầu: 0:30**

Tại block này, chúng ta sẽ bắt tay xử lý 3 vấn đề cốt lõi của log hệ thống: (1) gán mã định danh (Correlation ID) cho từng request để truy vết toàn trình, (2) làm giàu (enrich) metadata log để phục vụ bộ lọc/phân tích, và (3) lọc bỏ dữ liệu nhạy cảm (PII scrubbing) trước khi ghi log.

### Bước 1 — Correlation ID Middleware

Mở file **`app/middleware.py`**. Hiện tại correlation ID luôn là **`"MISSING"`**. Bạn cần hoàn thành 4 TODO:

```
class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Xóa context cũ để tránh leak giữa các request
        clear_contextvars()

        # 2. Lấy từ header hoặc tạo mới, format: req-<8 ký tự hex>
        correlation_id = request.headers.get(
            "x-request-id",
            f"req-{uuid.uuid4().hex[:8]}"
        )

        # 3. Bind vào structlog context — mọi log sau đó tự động có trường này
        bind_contextvars(correlation_id=correlation_id)

        request.state.correlation_id = correlation_id

        start = time.perf_counter()
        response = await call_next(request)

        # 4. Trả correlation ID và thời gian xử lý trong response header
        response.headers["x-request-id"] = correlation_id
        response.headers["x-response-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"

        return response

```

**Copy**

**Tại sao cần ****`clear_contextvars()`****?** Vì structlog dùng context variables (Python contextvars) để chia sẻ thông tin logs trong một luồng request.

> **💡 Tương tự trực quan:** Hãy tưởng tượng **contextvars** giống như một **chiếc túi xách đi kèm** với mỗi request. Khi request bắt đầu, ta cho vào túi các thông tin chung (như ID request, ID user). Mỗi hàm xử lý bên trong chỉ cần thò tay vào túi lấy ra dùng mà không cần phải truyền biến thủ công qua từng hàm.
>
> Tuy nhiên, nếu không gọi **`clear_contextvars()`** ở đầu mỗi request mới, luồng xử lý (thread/task) có thể dùng lại "chiếc túi cũ" của request trước đó, gây rò rỉ dữ liệu (data leakage).

**Lưu ý**·

#### Phần mở rộng (Không bắt buộc): Đảm bảo giữ Correlation ID khi xảy ra lỗi

Trong trường hợp API xảy ra lỗi hệ thống (ví dụ: lỗi **`tool_fail`** trả về HTTP 500), FastAPI mặc định sẽ tự tạo error response chung như **`{"detail": "RuntimeError"}`** và bỏ qua các header được gán trong Middleware thông thường. Việc này làm client (hoặc script **`load_test.py`**) nhận về correlation ID là **`None`**, gây khó khăn cho việc tra cứu log.

Để xử lý triệt để, bạn có thể thực hiện phần mở rộng sau:

1. Mở **`app/main.py`** và thêm một generic exception handler để đính kèm **`x-request-id`** vào header của response lỗi:
   ```
   from fastapi.responses import JSONResponse

   @app.exception_handler(Exception)
   async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
       correlation_id = getattr(request.state, "correlation_id", "unknown")
       return JSONResponse(
           status_code=500,
           content={"detail": type(exc).__name__},
           headers={"x-request-id": correlation_id},
       )

   ```
   **Copy**
2. Mở **`scripts/load_test.py`** và sửa dòng hiển thị kết quả (khoảng dòng 21) để ưu tiên đọc correlation ID từ header của response:
   ```
   # Thay dòng print cũ thành:
   cid = r.headers.get("x-request-id") or r.json().get("correlation_id", "None")
   print(f"[{r.status_code}] {cid} | {payload['feature']} | {latency:.1f}ms")

   ```
   **Copy**

### Bước 2 — Enrich log context

Mở file **`app/main.py`**, tìm hàm **`chat()`**. Thêm **`bind_contextvars`** **trước** dòng **`log.info("request_received", ...)`** để mọi log trong request đó tự động có metadata:

```
@app.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    # Enrich — tất cả log sau đây tự động có các trường này
    bind_contextvars(
        user_id_hash=hash_user_id(body.user_id),
        session_id=body.session_id,
        feature=body.feature,
        model="claude-sonnet-4-5",
        env=os.getenv("APP_ENV", "dev"),
    )

    log.info(
        "request_received",
        service="api",
        payload={"message_preview": summarize_text(body.message)},
    )
    # ... phần còn lại giữ nguyên

```

**Copy**

**Lưu ý:** Dùng **`hash_user_id(body.user_id)`** thay vì **`body.user_id`** trực tiếp — đây là lớp bảo vệ PII đầu tiên: chỉ log hash SHA-256 của user ID.

### Bước 3 — Bật PII Scrubbing

Mở file **`app/logging_config.py`**, tìm danh sách processors trong **`configure_logging()`**. Uncomment dòng **`scrub_event`**:

```
structlog.configure(
    processors=[
        merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True, key="ts"),
        scrub_event,  # ← Uncomment dòng này
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        JsonlFileProcessor(),
        structlog.processors.JSONRenderer(),
    ],
    # ...
)

```

**Copy**

**Thứ tự quan trọng:** **`scrub_event`** phải nằm **sau** **`TimeStamper`** (để không scrub timestamp) và **trước** **`JsonlFileProcessor`** + **`JSONRenderer`** (để PII được che trước khi ghi xuống file và trả về console).

### Bước 3b — Mở rộng phạm vi che PII (PII Scrubbing Extension)

Hàm **`scrub_event`** mặc định trong starter code chỉ che PII trong **`payload`** và **`event`**. Để đảm bảo an toàn tuyệt đối cho mọi trường log (như **`session_id`**, **`user_id_hash`**, v.v.), hãy thay thế hàm **`scrub_event`** trong **`app/logging_config.py`** bằng logic an toàn hơn dưới đây để duyệt qua mọi trường dạng string và dictionary:

```
def scrub_event(_: Any, __: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    for key, val in event_dict.items():
        if isinstance(val, str):
            event_dict[key] = scrub_text(val)
        elif isinstance(val, dict):
            event_dict[key] = {
                k: scrub_text(v) if isinstance(v, str) else v for k, v in val.items()
            }
    return event_dict

```

**Copy**

### Bước 4 — Thêm PII patterns

Mở file **`app/pii.py`**, thêm các regex pattern mới vào **`PII_PATTERNS`** để nhận diện Passport và Địa chỉ Việt Nam:

```
PII_PATTERNS: dict[str, str] = {
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    "phone_vn": r"(?:\+84|0)[ \.-]?\d{3}[ \.-]?\d{3}[ \.-]?\d{3,4}",
    "cccd": r"\b\d{12}\b",
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    # Thêm patterns mới:
    "passport": r"\b[A-Z]\d{7,8}\b",
    "address_vn": r"\b(?:số nhà|đường|phường|quận|huyện|tỉnh|thành phố)\b",
}

```

**Copy**

### Bước 5 — Liên kết Correlation ID vào Langfuse Trace

Để sau này ta có thể đối chiếu giữa Trace trên Langfuse và Log thô trong hệ thống, ta cần đính kèm **`correlation_id`** vào thông tin metadata của Trace.

Mở file **`app/agent.py`**, tìm hàm **`run()`**. Trong phần cập nhật trace trên Langfuse, hãy import và đính kèm **`correlation_id`** lấy từ **`structlog.contextvars`**:

```
        # Thêm import ở đầu file hoặc bên trong hàm:
        from structlog.contextvars import get_contextvars

        langfuse_client = get_langfuse_client()
        langfuse_client.update_current_trace(
            user_id=hash_user_id(user_id),
            session_id=session_id,
            tags=["lab", feature, self.model],
            metadata={"correlation_id": get_contextvars().get("correlation_id", "MISSING")},
        )

```

**Copy**

### Bước 6 — Bổ sung tỷ lệ lỗi (Error Rate) vào Metrics

Để phục vụ cho dashboard giám sát và alert rule cảnh báo lỗi hệ thống, ta cần tính toán được tỷ lệ lỗi (**`error_rate_pct`**) của API.

Mở file **`app/metrics.py`**, tìm hàm **`snapshot()`**. Hãy sửa đổi hàm này để tính toán tỷ lệ phần trăm lỗi từ tổng số request (request thành công **`TRAFFIC`** + request thất bại lưu trong **`ERRORS`**):

```
def snapshot() -> dict:
    total_errors = sum(ERRORS.values())
    total_requests = TRAFFIC + total_errors
    error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0.0

    return {
        "traffic": TRAFFIC,
        "latency_p50": percentile(REQUEST_LATENCIES, 50),
        "latency_p95": percentile(REQUEST_LATENCIES, 95),
        "latency_p99": percentile(REQUEST_LATENCIES, 99),
        "avg_cost_usd": round(mean(REQUEST_COSTS), 4) if REQUEST_COSTS else 0.0,
        "total_cost_usd": round(sum(REQUEST_COSTS), 4),
        "tokens_in_total": sum(REQUEST_TOKENS_IN),
        "tokens_out_total": sum(REQUEST_TOKENS_OUT),
        "error_rate_pct": round(error_rate, 2),  # ← Thêm trường này
        "error_breakdown": dict(ERRORS),
        "quality_avg": round(mean(QUALITY_SCORES), 4) if QUALITY_SCORES else 0.0,
    }

```

**Copy**

### Kiểm tra kết quả

Xóa log cũ để tránh dữ liệu cũ làm sai kết quả chấm điểm của script validator:

**macOS/Linux:**

```
rm -f data/logs.jsonl

```

**Copy**

**Windows PowerShell:**

```
Remove-Item -Path data/logs.jsonl -ErrorAction SilentlyContinue

```

**Copy**

Khởi động lại Uvicorn:

```
# Bấm Ctrl+C ở Terminal 1 để tắt uvicorn cũ, rồi chạy lại:
uvicorn app.main:app --reload --env-file .env

```

**Copy**

Terminal 2:

```
python scripts/load_test.py
python scripts/validate_logs.py

```

**Copy**

Mục tiêu: **score ≥ 80/100**. Kiểm tra cụ thể:

- **`correlation_id`** không còn **`"MISSING"`** → format **`req-<8hex>`**
- Các trường **`user_id_hash`**, **`session_id`**, **`feature`**, **`model`** xuất hiện trong log **`request_received`**
- Email và số điện thoại trong sample queries đã bị thay bằng **`[REDACTED_...]`**

Kiểm tra PII bằng tay:

```
grep -i "@" data/logs.jsonl    # Không nên có kết quả
grep "4111" data/logs.jsonl    # Không nên có kết quả
grep "REDACTED" data/logs.jsonl  # Phải có kết quả

```

**Copy**

**Tự kiểm**·

#### ✅ CHECKPOINT CP1 — Structured Logging, Correlation ID & PII

**Tiêu chí nghiệm thu:**

- **Kết quả kiểm tra:** Chạy **`python scripts/validate_logs.py`** đạt tối thiểu **`80/100`** điểm và **`python -m pytest -q`** trả về kết quả pass hoàn toàn.
- **Bằng chứng (Evidence):** Ảnh chụp màn hình điểm log validator và một đoạn log chứa correlation ID kèm chuỗi che thông tin **`[REDACTED_...]`** lưu trong thư mục **`submission/evidence/`**.
- **Câu hỏi phản biện:** Mô tả sự khác biệt lớn nhất giữa log baseline (CP0) và log sau khi làm xong CP1. Tại sao bước gọi **`clear_contextvars()`** ở đầu middleware lại mang tính bắt buộc?

---
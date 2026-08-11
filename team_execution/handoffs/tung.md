# Báo Cáo Bàn Giao (Handoff) - Track Langfuse Tracing & Prompt Versioning

**Người thực hiện**: Nguyễn Hữu Khánh Tùng (Tùng)  
**Nhánh Git**: `tungnhoc` (Commit message: `done Unit Test`)  
**Ngày hoàn thành**: 11/08/2026  

---

## 1. Tóm Tắt Kết Quả Công Việc
Đã hoàn thành toàn bộ các yêu cầu của Track **Langfuse Tracing & Prompt Versioning** cho Lab 13:
1. **Correlation ID Integration**: Đã tích hợp thành công `correlation_id` từ `structlog.contextvars` vào `metadata` của Langfuse Trace (`langfuse_client.update_current_trace`), phục vụ luồng đối chiếu 1-1 giữa Log và Trace.
2. **Local Fallback Transparency**: Đảm bảo tính minh bạch khi không có Langfuse SDK (`source="local"`) hoặc khi fetch prompt thất bại (`source="local-fallback"`), không báo gian dối là Managed Prompt.
3. **Automated Testing**: Viết bổ sung các unit test kiểm thử correlation ID và prompt versioning. 100% test cases đã pass (`9/9 PASSED`).
4. **Prompt Versioning & Rollback**: Thiết lập thành công Managed Prompt `day13-chat` trên Langfuse UI với 2 phiên bản (v1: `baseline`/`production`, v2: `candidate`), chạy thử nghiệm và thu thập đầy đủ bằng chứng thao tác Rollback.

---

## 2. Danh Sách Các File Đã Thay Đổi / Tạo Mới

### Files Đã Sửa / Tạo (Ownership của Tùng):
- `app/agent.py`: Trích xuất `correlation_id` từ `structlog.contextvars` và truyền vào trace metadata.
- `tests/test_agent_prompt_trace.py`: Cập nhật mock client test kiểm tra `correlation_id`.
- `tests/test_trace_correlation.py`: (Tạo mới) Unit test kiểm thử trường hợp có `correlation_id` và trường hợp contextvars trống (`MISSING`).

### Files Bằng Chứng (Evidence):
- `submission/evidence/tracing/trace-list.png`: Danh sách 10+ traces trên Langfuse Dashboard.
- `submission/evidence/tracing/trace-waterfall.png`: Chi tiết 1 Trace Waterfall Tree view.
- `submission/evidence/tracing/prompt-versions-traces.png`: Màn hình quản lý 2 phiên bản Prompt (v1 & v2).
- `submission/evidence/tracing/prompt-rollback-evidence.png`: Màn hình thao tác Rollback nhãn `production`.

---

## 3. Kết Quả Kiểm Thử Tự Động (Unit Tests)

Đã khởi chạy kiểm thử thành công bằng lệnh:
```powershell
.venv\Scripts\python.exe -m pytest tests/test_agent_prompt_trace.py tests/test_prompt_management.py tests/test_tracing_adapter.py tests/test_trace_correlation.py -v
```

**Kết quả**: `9 passed in 1.04s (100% SUCCESS)`

```text
tests/test_agent_prompt_trace.py::test_agent_links_prompt_version_to_trace_and_generation PASSED
tests/test_prompt_management.py::test_local_prompt_fallback_keeps_lab_runnable_without_langfuse PASSED
tests/test_prompt_management.py::test_langfuse_prompt_version_and_label_are_resolved PASSED
tests/test_prompt_management.py::test_prompt_fetch_failure_uses_visible_local_fallback PASSED
tests/test_prompt_management.py::test_sdk_fallback_is_not_reported_as_managed_prompt PASSED
tests/test_tracing_adapter.py::TracingAdapterTests::test_adapter_uses_the_installed_langfuse_v3_api PASSED
tests/test_tracing_adapter.py::TracingAdapterTests::test_tracing_is_disabled_without_both_keys PASSED
tests/test_trace_correlation.py::test_trace_metadata_includes_correlation_id_when_present PASSED
tests/test_trace_correlation.py::test_trace_metadata_defaults_to_missing_when_correlation_id_absent PASSED
```

---

## 4. Hướng Dẫn Tích Hợp Cho Lead (Vũ)
1. Nhánh `tungnhoc` đã được push sẵn lên GitHub (`origin/tungnhoc`). Vũ chỉ cần merge Pull Request của `tungnhoc` vào nhánh `main`.
2. Khi khởi chạy nghiệm thu tổng thể (`scripts/load_test.py`), hệ thống sẽ tự động ghi lại cả Log lẫn Trace có chung `correlation_id` và đính kèm `prompt_version` tương ứng.

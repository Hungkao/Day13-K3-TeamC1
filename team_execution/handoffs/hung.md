# Handoff Track Metrics, Dashboard, SLO, Alerts và Runbook — Hưng

## 1. Danh sách file đã tác động

### File đã chỉnh sửa trong Repo
- `app/metrics.py`: Thêm chỉ số `error_rate_pct` vào `snapshot()` và xử lý trường hợp chia cho 0.
- `tests/test_metrics.py`: Bổ sung 4 unit test bao phủ toàn bộ các trường hợp biên của `snapshot()` (zero state, only success, only errors, mixed).
- `config/slo.yaml`: Hoàn thiện mục tiêu SLI/SLO và loại bỏ các ghi chú placeholder.
- `config/alert_rules.yaml`: Thay toàn bộ TODO bằng 3 alert rules dựa trên triệu chứng (Symptom-based & SLO-based).
- `docs/alerts.md`: Điền đầy đủ Runbook cho cả 3 alert bao gồm ảnh hưởng người dùng, 3 bước kiểm tra đầu tiên, giải pháp khắc phục tạm thời (mitigation) và owner.

### File tạo mới
- `dashboard/app.py`: Ứng dụng runtime CLI đọc `data/logs.jsonl` và render đúng 6 panel dashboard theo contract.
- `team_execution/handoffs/hung.md`: File handoff này.

---

## 2. Công thức & Contract đã áp dụng

### 2.1 Metrics Error Rate (`app/metrics.py`)
$$\text{total\_errors} = \sum(\text{ERRORS.values()})$$
$$\text{total\_requests} = \text{TRAFFIC} + \text{total\_errors}$$
$$\text{error\_rate\_pct} = \text{round}\left(\frac{\text{total\_errors}}{\text{total\_requests}} \times 100, 2\right) \quad (\text{nếu } \text{total\_requests} > 0 \text{ else } 0.0)$$

### 2.2 Dashboard Contract (`config/dashboard.yaml`)
Đảm bảo đúng 6 panel theo quy định:
1. **Latency percentiles**: P50, P95, P99 (Threshold: P95 <= 3000 ms)
2. **Request traffic**: Count & rate per minute
3. **Error rate and breakdown**: `error_rate_pct` & breakdown by `error_type` (Threshold: <= 2.0%)
4. **Cost over time**: Sum by minute & total USD (Threshold: <= $2.50 USD)
5. **Input and output tokens**: Sum `tokens_in` & `tokens_out` (Threshold: <= 50,000)
6. **Quality proxy**: Mean `quality_score` (Threshold: >= 0.75)

### 2.3 Alert Rules (`config/alert_rules.yaml` & `docs/alerts.md`)
1. `HighLatencyP95` (Critical): P95 latency > 3000ms over 2m window.
2. `HighErrorRate` (Critical): Error rate > 2% over 3m window.
3. `HighCostBurnRate` (Warning): Total cost > $2.5 USD over 60m window.

---

## 3. Lệnh kiểm tra & Kết quả Test/Validator

### 3.1 Chạy Dashboard Validator Contract
```powershell
python scripts/validate_dashboard.py
```
**Kết quả**: `HỢP LỆ: 6/6 panel có trong dashboard contract.`

### 3.2 Chạy Pytest
```powershell
python -m pytest -q
```
**Kết quả**: `26 passed, 2 warnings in 4.61s` (Tất cả test cases của `test_metrics.py` và `test_dashboard_validator.py` đều pass 100%).

### 3.3 Chạy Dashboard Runtime Viewer
```powershell
python dashboard/app.py
```
**Kết quả**: Render thành công bảng tổng hợp 6 panel từ `data/logs.jsonl`.

---

## 4. Cách chạy Dashboard Runtime

Khi app FastAPI hoạt động và có log sinh ra tại `data/logs.jsonl`:
```powershell
# Chạy hiển thị Dashboard runtime
python dashboard/app.py
```
Hoặc chỉ định đường dẫn log tùy chọn:
```powershell
python dashboard/app.py path/to/logs.jsonl
```

---

## 5. Phần Runtime chưa thể xác nhận & Rủi ro ngoài Ownership

- **Phần Runtime chưa thể chụp ảnh thật**: Do `data/logs.jsonl` chưa được tạo tại bước dev độc lập, ảnh chụp Dashboard runtime thật với 6 panel đầy đủ số liệu sẽ được thu thập sau khi Lead (Vũ) kích hoạt server và chạy `load_test.py` / `inject_incident.py`.
- **Rủi ro ngoài Ownership**: Cần đảm bảo các log `response_sent` do Phong bổ sung chứa đầy đủ các trường `latency_ms`, `cost_usd`, `tokens_in`, `tokens_out`, `quality_score` đúng tên field để Dashboard runtime và Metrics tổng hợp khớp 100%.

# Evidence điều tra Challenge K3

## Phạm vi

- Challenge ID: `day13-k3-observability-v1`
- Incident: `rag_slow`
- Feature bị ảnh hưởng: `refund`
- Ngưỡng latency chính thức: `2000 ms`
- Ngày nghiệm thu: `2026-08-11`

## Metrics — baseline so với incident

Hai lượt batch dùng cùng 5 query chính thức và concurrency 5.

| Chỉ số | Baseline (`rag_slow=false`) | Challenge (`rag_slow=true`) | Thay đổi |
|---|---:|---:|---:|
| Latency P50 | 181 ms | 2702 ms | +2521 ms |
| Latency P95 | 198 ms | 2707 ms | +2509 ms / +1267.2% |
| Latency P99 | 198 ms | 2707 ms | +2509 ms |
| Error rate | 0% | 0% | Không đổi |
| Quality average | 0.86 | 0.86 | Không đổi |
| Total cost | $0.0090 | $0.0110 | +$0.0020 |

P95 challenge `2707 ms` vượt ngưỡng challenge `2000 ms`. Dashboard contract dùng SLO P95 `<= 3000 ms`, nên panel vẫn hiển thị `OK`; đây là hai ngưỡng có mục đích khác nhau.

Nguồn dữ liệu:

- `submission/evidence/incident/baseline-logs.jsonl`
- `submission/evidence/incident/challenge-logs.jsonl`

## Trace và retriever span

Request xác minh trace được chạy với cùng incident, feature và input chính thức:

- Trace ID: `8ffc1862d57f573a234a59f49eab5da2`
- Correlation ID: `req-feed1303`
- Session: `k3-challenge-retriever`
- Prompt: `day13-chat` v1 / `production`
- Generation `run`: `4.060 s`
- Observation `retrieve-context`: `2.501 s`, parent trực tiếp của generation `run`
- Retriever metadata: `feature=refund`, `incident_rag_slow=true`
- Retriever input chỉ chứa query preview đã qua PII scrub; output chỉ chứa `document_count=1`.

Observation `retrieve-context` chiếm phần lớn thời gian xử lý và chỉ rõ bottleneck nằm ở retrieval, thay vì chỉ khoanh vùng ở toàn bộ agent run.

## Log correlation

Log cùng request với trace:

```json
{"correlation_id":"req-feed1303","event":"request_received","feature":"refund","session_id":"k3-challenge-retriever","payload":{"message_preview":"What is your refund policy?"}}
{"correlation_id":"req-feed1303","event":"response_sent","feature":"refund","latency_ms":4058,"quality_score":0.9,"session_id":"k3-challenge-retriever"}
```

File đầy đủ: `submission/evidence/incident/retriever-trace-log.jsonl`.

Batch challenge có 5/5 request thành công, latency `2687–2707 ms`, không có `request_failed`.

## Root cause

`config/challenge.json` bật `rag_slow`. Trong `app/mock_rag.py`, `retrieve()` gọi `time.sleep(2.5)` khi incident bật. Blocking call nằm trong đường xử lý endpoint async nên:

1. `retrieve-context` kéo dài khoảng 2.5 giây.
2. Event loop bị chặn và các request concurrency bị xử lý gần như nối tiếp.
3. Error rate và quality không đổi vì đây là latency incident, không phải correctness incident.

## Fix action và preventive measure

Mitigation đã thực hiện: tắt incident; `/health` xác nhận `rag_slow=false`.

Fix production đề xuất:

- Dùng async retrieval; với mock delay dùng `await asyncio.sleep`, với thư viện sync dùng thread pool.
- Đặt timeout và fallback an toàn khi retrieval upstream chậm.

Phòng ngừa đã/đề xuất:

- Đã instrument observation ổn định `retrieve-context` và metadata incident/feature.
- Dùng anomaly automation với ngưỡng operational `P95 > 2000 ms` bên cạnh SLO 3000 ms.
- Thêm concurrency regression test trong vòng cải tiến tiếp theo.
- Theo dõi timeout rate, circuit breaker và retrieval latency độc lập.

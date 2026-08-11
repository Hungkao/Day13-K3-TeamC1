# Bonus — Cost optimization

## Phương pháp

1. Bật `cost_spike` và chạy 10 request từ `data/sample_queries.jsonl` với concurrency 5.
2. Ghi nhận before từ `cost-before.jsonl`.
3. Thêm `MAX_OUTPUT_TOKENS=240`; `FakeLLM` giới hạn output sau khi incident nhân token.
4. Khởi động lại API, bật lại cùng incident và chạy lại 10 request.
5. Ghi nhận after từ `cost-after.jsonl`.

## Kết quả

| Chỉ số | Before | After | Thay đổi |
|---|---:|---:|---:|
| Request thành công | 10 | 10 | Không đổi |
| Total cost | $0.0778 | $0.0370 | giảm $0.0408 / 52.4% |
| Output tokens | 5120 | 2400 | giảm 2720 / 53.1% |
| Error rate | 0% | 0% | Không đổi |
| Quality proxy | 0.88 | 0.88 | Không đổi |

Giới hạn 240 cao hơn output bình thường 80–180 token, nên không mở rộng hoặc cắt response bình thường; nó chỉ chặn output bất thường do `cost_spike`.

Evidence:

- `submission/evidence/bonus/cost-before.jsonl`
- `submission/evidence/bonus/cost-after.jsonl`
- `submission/evidence/bonus/cost-before-after.png`

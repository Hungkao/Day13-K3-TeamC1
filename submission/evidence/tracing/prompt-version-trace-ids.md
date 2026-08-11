# Prompt version trace evidence — 2026-08-11

## Prompt state đã xác minh qua Langfuse API

| Version | Labels | Nội dung mở đầu |
|---|---|---|
| v1 | `baseline`, `production` | `Feature={{feature}}` |
| v2 | `candidate` | `Answer briefly and clearly.` |

Langfuse còn lưu v3 trong lịch sử vì một candidate mới được tạo trước khi phát hiện v2 đã tồn tại nhưng chưa gắn label. Label `candidate` đã được chuyển về đúng v2; v3 không mang `baseline`, `candidate` hay `production` và không dùng trong so sánh.

## Cùng input chạy qua hai version

- Input: `What is your refund policy?`
- Feature: `refund`
- Session: `k3-prompt-v1-v2`
- User: cùng một user hash do app tạo; không lưu raw user ID trong evidence.

| Nhánh prompt | Trace ID | Correlation ID | Metadata xác minh |
|---|---|---|---|
| Baseline v1 | `c7af89d1fde84429c458ca092dd97d47` | `req-a11ce001` | `prompt_name=day13-chat`, `prompt_label=baseline`, `prompt_version=1`, `prompt_source=langfuse` |
| Candidate v2 | `3824f432373f555607e5450e008b149d` | `req-a11ce002` | `prompt_name=day13-chat`, `prompt_label=candidate`, `prompt_version=2`, `prompt_source=langfuse` |

Hai trace được đọc lại từ Langfuse API sau khi client `flush()`. Không dùng ID tự tạo hoặc placeholder.

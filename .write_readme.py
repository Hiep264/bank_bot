from pathlib import Path

text = r'''# Agent Chat API

## Tổng quan

Đây là một backend API FastAPI cho một ứng dụng chat có khả năng lưu cuộc hội thoại, tạo summary định kỳ, và gửi ngữ cảnh summary vào prompt khi gọi LLM.

## Kiến trúc chính

- `app/main.py`
  - Khởi tạo FastAPI app.
  - Thêm middleware CORS và mount router cho chat + conversations.
- `app/api/chat.py`
  - Endpoint POST `/chat` nhận tin nhắn người dùng.
  - Quản lý mô hình cuộc hội thoại: tạo conversation mới hoặc lấy conversation hiện tại.
  - Lưu tin nhắn user, lấy message gần nhất, gọi LLM để tạo trả lời.
  - Tạo summary mỗi khi số tin nhắn đạt bội số của `SUMMARY_INTERVAL` (hiện là 6).
- `app/api/conversations.py`
  - Endpoint tạo conversation mới, lấy danh sách conversations, lấy messages theo conversation.
- `app/services/conversation_service.py`
  - Xử lý đọc/ghi dữ liệu vào Supabase.
  - Lưu messages, cập nhật conversation title/summary, truy vấn số lượng message.
- `app/services/llm_service.py`
  - Tạo prompt gửi tới LLM.
  - Nếu conversation đã có `summary`, chèn summary vào phần `system` trước khi gửi request.
- `app/services/summary_service.py`
  - Gom toàn bộ cuộc hội thoại thành một prompt cho Gemini.
  - Yêu cầu tóm tắt các chủ đề chính, mục tiêu, quyết định, ưu tiên; bỏ qua small talk.
- `app/db/supabase.py`
  - Khởi tạo client Supabase từ biến môi trường.
- `app/core/config.py`
  - Định nghĩa cấu hình môi trường cho LLM, Gemini, Supabase và frontend.

## Luồng hoạt động `/chat`

1. Nhận request POST `/chat` với payload có `message` và `conversation_id` (có thể null).
2. Nếu chưa có `conversation_id`, tạo mới conversation.
3. Lưu message user vào bảng `messages` với `role='user'`.
4. Lấy tất cả messages của conversation và trích recent messages.
5. Lấy `summary` hiện tại từ conversation.
6. Gọi `llm_service.generate_reply(...)` để trả về reply, trong đó summary được chèn vào system prompt nếu tồn tại.
7. Lưu reply của assistant vào bảng `messages`.
8. Nếu là tin nhắn thứ 6, 12, 18, ... thì gọi `summary_service.summarize(existing_messages)` và cập nhật field `summary` của conversation.
9. Cập nhật thông tin conversation.

## Cách summary được thực hiện

- Summary được tạo trong `app/services/summary_service.py`.
- Mỗi lần `message_count` đạt bội số của `SUMMARY_INTERVAL` (6), `chat.py` sẽ gọi `summary_service.summarize(existing_messages)`.
- Summary sau đó được lưu vào trường `summary` của record conversation.
- Khi gọi LLM để tạo trả lời, `llm_service.py` sẽ dùng summary hiện tại làm ngữ cảnh bổ sung.

## Mô hình dữ liệu và storage

- Supabase dùng 2 bảng chính:
  - `conversations`: lưu metadata conversation, title, summary, updated_at.
  - `messages`: lưu các tin nhắn với `conversation_id`, `role`, `content`, `message_order`.
- `ConversationService` đọc/ghi các bảng này.

## Các file chính

- `app/main.py`
- `app/api/chat.py`
- `app/api/conversations.py`
- `app/services/conversation_service.py`
- `app/services/llm_service.py`
- `app/services/summary_service.py`
- `app/db/supabase.py`
- `app/core/config.py`

## Biến môi trường quan trọng

- `LLAMA_CPP_URL`: URL của API LLM nội bộ.
- `MODEL_NAME`: tên model chat của LLM.
- `GEMINI_API_KEY`: API key cho Google Gemini summary.
- `SUPABASE_URL`, `SUPABASE_KEY`: cấu hình kết nối Supabase.
- `FRONTEND_URL`: URL frontend (hiện không dùng trực tiếp trong README này nhưng được định nghĩa trong config).

## Chạy ứng dụng

Bạn có thể chạy server bằng Uvicorn từ thư mục gốc:

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Sau đó, gọi endpoint `/chat` để chat và endpoint `/conversations` để quản lý cuộc hội thoại.

## Ghi chú

- Summary tự động cập nhật theo `SUMMARY_INTERVAL = 6` trong `app/api/chat.py`.
- `app/services/llm_service.py` sử dụng HTTP API của LLM và chèn `summary` vào prompt nếu có.
- `app/services/summary_service.py` dùng Google Gemini qua `google.generativeai` để tạo bản tóm tắt.
'''
Path('README.md').write_text(text, encoding='utf-8')


# 🤖 Bot Telegram Nhắc Hạn Tài Khoản

Bot này sẽ:
- Gửi danh sách tài khoản sắp hết hạn (0 hoặc 1 ngày) vào kênh Telegram mỗi sáng lúc 8h ⏰
- Trả lời lệnh `/hethan` để hiển thị danh sách sắp hết hạn
- Phản hồi mặc định với hướng dẫn nếu người dùng gửi nội dung khác

## 🚀 Triển khai trên Railway

### 1. Chuẩn bị biến môi trường

| Tên biến            | Mô tả |
|---------------------|-------|
| `BOT_TOKEN`         | Token Telegram bot từ [@BotFather](https://t.me/BotFather) |
| `CHANNEL_ID`        | ID kênh hoặc chat_id người nhận. Ví dụ: `@tenkenhcuaban` hoặc `-1001234567890` |
| `RAILWAY_URL`       | Domain Railway của bạn (ví dụ: `https://tenapp.up.railway.app`) |
| `GOOGLE_CREDENTIALS`| Toàn bộ nội dung file `creds.json` của Google Service Account, dán dưới dạng JSON |

> 📌 Sheet Google phải chia sẻ quyền cho email trong `client_email` từ `creds.json`

---

### 2. Cấu trúc Google Sheet

Sheet cần có các cột (ít nhất 16 cột), dữ liệu nằm từ dòng thứ 2. Các cột cần:
- `C` – Tên (lọc theo "Khuyên")
- `F` – Tài khoản
- `I` – Ngày đăng ký
- `J` – Ngày hết hạn (`YYYY-MM-DD`)
- `P` – Giá bán

---

### 3. Cài đặt (nếu chạy cục bộ)

```bash
pip install python-telegram-bot==20.7 gspread oauth2client httpx
```

---

### 4. Tệp chính

- `main.py` – điều khiển bot, xử lý webhook
- `utils.py` – đọc dữ liệu từ Google Sheet
- `README.md` – hướng dẫn triển khai

---

### 5. Giao diện Bot

- `/hethan`: trả về danh sách tài khoản sắp hết hạn
- Tin nhắn khác: phản hồi mặc định với hướng dẫn

---

### 💬 Ví dụ tin nhắn bot gửi:

```
[📌] *Danh sách tài khoản sắp hết hạn:*

📱 Facebook
👤 abc@example.com
🗓️ Reg: 2024-04-10 | 💰 Giá: 100k
⏰ Exp: 2025-04-23 (Còn 1 ngày)
```

---

> ✨ Cần thêm tính năng như `/giahan`, thống kê, ghim tin nhắn? Nhắn mình để mở rộng!

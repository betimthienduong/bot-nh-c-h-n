# 🤖 Bot Telegram Nhắc Hạn Tài Khoản

Bot này sẽ:
- Gửi danh sách tài khoản sắp hết hạn (còn lại 0 hoặc 1 ngày) vào kênh Telegram mỗi sáng lúc 8h ⏰
- Trả lời lệnh `/hethan` để hiển thị danh sách sắp hết hạn
- Phản hồi mặc định với hướng dẫn nếu người dùng gửi nội dung khác

---

## 🚀 Triển khai trên Railway

### 1. Chuẩn bị biến môi trường

| Tên biến            | Mô tả |
|---------------------|-------|
| `BOT_TOKEN`         | Token Telegram bot từ [@BotFather](https://t.me/BotFather) |
| `CHANNEL_ID`        | ID kênh hoặc chat_id người nhận. Ví dụ: `@tenkenhcuaban` hoặc `-1001234567890` |
| `RAILWAY_URL`       | Domain Railway của bạn (ví dụ: `https://tenapp.up.railway.app`) |
| `GOOGLE_CREDENTIALS`| Toàn bộ nội dung file `creds.json` của Google Service Account, dán dưới dạng JSON (1 dòng) |

> 📌 Sheet Google phải chia sẻ quyền chỉnh sửa cho email trong `client_email` từ file `creds.json`.

---

### 2. Cấu trúc Google Sheet

- Sheet cần có ít nhất 16 cột (từ A đến P)
- Dữ liệu bắt đầu từ dòng thứ 2
- Các cột bắt buộc gồm:

| Cột | Ý nghĩa           |
|-----|--------------------|
| `C` | Nền tảng (ví dụ: `FB Khuyên`, `ZL Khuyên`...) — bot lọc theo `"Khuyên"` |
| `F` | Tài khoản cần nhắc |
| `I` | Ngày đăng ký       |
| `J` | Ngày hết hạn       |
| `L` | Số ngày còn lại    |
| `P` | Giá bán            |

---

### 3. Cài đặt (nếu chạy cục bộ)

```bash
pip install python-telegram-bot==20.7 gspread oauth2client httpx

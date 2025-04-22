import os
import json
import asyncio
from datetime import datetime, timedelta, time

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler,
    filters, Defaults, AIORateLimiter
)

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SHEET_URL = os.getenv("SHEET_URL")
WORKSHEET_NAME = os.getenv("SHEET_SHEET_NAME", "chatgpt")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_CHAT_ID = os.getenv("CHANNEL_CHAT_ID")

defaults = Defaults(parse_mode="Markdown")
app = ApplicationBuilder()\
    .token(BOT_TOKEN)\
    .rate_limiter(AIORateLimiter())\
    .post_init(lambda app: setattr(app, "job_queue", app.job_queue))\
    .build()

def connect_sheet():
    credentials_json = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_json, SCOPE)
    client = gspread.authorize(creds)
    return client.open_by_url(SHEET_URL).worksheet(WORKSHEET_NAME)

def extract_expiring_accounts():
    sheet = connect_sheet()
    rows = sheet.get_all_records()
    today = datetime.now().date()
    results = []
    for row in rows:
        try:
            if row.get("Tên") != "Khuyên":
                continue
            expire_date = datetime.strptime(str(row["Hết hạn"]), "%Y-%m-%d").date()
            days_left = (expire_date - today).days
            if days_left in (0, 1):
                results.append({
                    "nền tảng": row.get("Nền tảng", ""),
                    "dịch vụ": row.get("Dịch vụ", ""),
                    "account": row.get("Account", ""),
                    "date": row.get("Date reg", ""),
                    "giá": row.get("Giá bán", ""),
                    "hết hạn": str(expire_date),
                    "còn": days_left
                })
        except:
            continue
    return results

def format_message(accounts):
    if not accounts:
        return "✅ Không có tài khoản nào sắp hết hạn."
    lines = ["[📌] *Danh sách tài khoản sắp hết hạn:*\n"]
    for acc in accounts:
        lines.append(
            f"📱 *{acc['nền tảng']}* - {acc['dịch vụ']}\n"
            f"👤 `{acc['account']}`\n"
            f"🗓️ Đăng ký: {acc['date']} | 💰 Giá: {acc['giá']}\n"
            f"⏰ Hết hạn: {acc['hết hạn']} (Còn {acc['còn']} ngày)\n"
        )
    return "\n".join(lines)

async def notify_expiring(context: ContextTypes.DEFAULT_TYPE):
    data = extract_expiring_accounts()
    message = format_message(data)
    await context.bot.send_message(chat_id=CHANNEL_CHAT_ID, text=message)

async def on_demand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = extract_expiring_accounts()
    message = format_message(data)
    await update.message.reply_text(message)

async def reply_to_any_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Gửi /hethan để xem tài khoản sắp hết hạn nha!")

async def main():
    app.add_handler(CommandHandler("hethan", on_demand))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_to_any_message))

    hour = int(os.getenv("REMIND_HOUR", 8))
    minute = int(os.getenv("REMIND_MINUTE", 0))
    app.job_queue.run_daily(notify_expiring, time=time(hour=hour, minute=minute))

    await app.bot.set_webhook(url=os.getenv("WEBHOOK_URL") + "/webhook")
    await app.run_webhook(listen="0.0.0.0", port=int(os.getenv("PORT", 8080)), url_path="webhook")

if __name__ == "__main__":
    asyncio.run(main())

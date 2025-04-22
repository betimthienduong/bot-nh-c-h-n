
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
)
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from datetime import datetime, timedelta, time

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ECU9jLUHFeAqpH5UggdFjkiEeiqc6F_ZHGD9Rs8Gc/edit"
WORKSHEET_NAME = "chatgpt"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_CHAT_ID = os.getenv("CHANNEL_CHAT_ID")

app = ApplicationBuilder().token(BOT_TOKEN).build()

def connect_sheet():
    credentials_raw = os.getenv("GOOGLE_CREDENTIALS")
    credentials_json = json.loads(credentials_raw)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_json, SCOPE)
    client = gspread.authorize(creds)
    return client.open_by_url(SHEET_URL).worksheet(WORKSHEET_NAME)

def extract_expiring_accounts():
    sheet = connect_sheet()
    rows = sheet.get_all_records()
    today = datetime.now().date()
    expiring_accounts = []

    for row in rows:
        try:
            if row.get("Tên") != "Khuyên":
                continue
            expire_date = datetime.strptime(str(row["Hết hạn"]), "%Y-%m-%d").date()
            delta = (expire_date - today).days
            if delta in (0, 1):
                expiring_accounts.append({
                    "nền tảng": row.get("Nền tảng", ""),
                    "dịch vụ": row.get("Dịch vụ", ""),
                    "account": row.get("Account", ""),
                    "date": row.get("Date reg", ""),
                    "giá": row.get("Giá bán", ""),
                    "hết hạn": str(expire_date),
                    "còn": delta
                })
        except Exception:
            continue
    return expiring_accounts

def format_message(accounts):
    if not accounts:
        return "✅ Không có tài khoản nào sắp hết hạn."

    text = "[📌] *Danh sách tài khoản sắp hết hạn:*
"
    for acc in accounts:
        text += (
            f"
📱 *{acc['nền tảng']}* - {acc['dịch vụ']}
"
            f"👤 `{acc['account']}`
"
            f"🗓️ Đăng ký: {acc['date']} | 💰 Giá: {acc['giá']}
"
            f"⏰ Hết hạn: {acc['hết hạn']} (Còn {acc['còn']} ngày)
"
        )
    return text

async def notify_expiring(context: ContextTypes.DEFAULT_TYPE):
    accounts = extract_expiring_accounts()
    message = format_message(accounts)
    await context.bot.send_message(chat_id=CHANNEL_CHAT_ID, text=message, parse_mode="Markdown")

async def on_demand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = extract_expiring_accounts()
    message = format_message(accounts)
    await update.message.reply_text(message, parse_mode="Markdown")

async def reply_to_any_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Mình là bot nhắc hạn. Gửi /hethan để xem tài khoản sắp hết hạn nhé!")

import asyncio

async def main():
    app.add_handler(CommandHandler("hethan", on_demand))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_to_any_message))
    hour = int(os.getenv("REMIND_HOUR", "8"))
    minute = int(os.getenv("REMIND_MINUTE", "0"))
    app.job_queue.run_daily(notify_expiring, time=time(hour=hour, minute=minute))
    await app.bot.set_webhook(url=os.getenv("WEBHOOK_URL") + "/webhook")
    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        url_path="webhook"
    )

if __name__ == "__main__":
    asyncio.run(main())

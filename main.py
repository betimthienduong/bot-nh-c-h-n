import os
import json
import datetime
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

# Google Sheets
SHEET_NAME = 'Trình đơn'
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def connect_sheet():
    credentials_raw = os.getenv("GOOGLE_CREDENTIALS")
    if not credentials_raw:
        raise ValueError("Thiếu biến môi trường GOOGLE_CREDENTIALS")
    
    credentials_json = json.loads(credentials_raw)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_json, SCOPE)
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).sheet1

def extract_expiring_accounts():
    sheet = connect_sheet()
    rows = sheet.get_all_values()[1:]

    result = []
    for row in rows:
        if len(row) < 16:
            continue
        platform = row[2].strip()
        days_left_str = row[11].strip()
        try:
            days_left = int(days_left_str)
        except:
            continue
        if platform not in ["FB Khuyên", "ZL Khuyên"]:
            continue
        if days_left in [0, 1]:
            result.append({
                "nền tảng": platform,
                "dịch vụ": row[3],
                "account": row[6],
                "date_reg": row[9],
                "giá_bán": row[15]
            })
    return result

async def notify_expiring(context: ContextTypes.DEFAULT_TYPE):
    accounts = extract_expiring_accounts()
    if not accounts:
        return
    text = "[📌] *Danh sách tài khoản sắp hết hạn:*\n"
    for acc in accounts:
        text += f"\n• *{acc['nền tảng']}* | {acc['dịch vụ']}\n➡️ `{acc['account']}`\n📅 Đăng ký: {acc['date_reg']} | 💰 Giá: {acc['giá_bán']}\n"
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, parse_mode="Markdown")

async def on_demand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = extract_expiring_accounts()
    if not accounts:
        await update.message.reply_text("✅ Không có tài khoản nào sắp hết hạn.")
        return
    text = "[📌] *Danh sách tài khoản sắp hết hạn:*\n"
    for acc in accounts:
        text += f"\n• *{acc['nền tảng']}* | {acc['dịch vụ']}\n➡️ `{acc['account']}`\n📅 Đăng ký: {acc['date_reg']} | 💰 Giá: {acc['giá_bán']}\n"
    await update.message.reply_text(text, parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("hethan", on_demand))
    app.job_queue.run_daily(notify_expiring, time=datetime.time(hour=8, minute=0))
    app.run_polling()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()

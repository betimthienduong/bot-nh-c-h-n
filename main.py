import datetime
import os
import logging
import gspread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from oauth2client.service_account import ServiceAccountCredentials

# Cấu hình Google Sheet
SHEET_NAME = 'Trình đơn'  # Đổi nếu khác
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CRED_FILE = 'credentials.json'

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

def connect_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CRED_FILE, SCOPE)
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).sheet1

def extract_expiring_accounts():
    sheet = connect_sheet()
    rows = sheet.get_all_values()[1:]  # Bỏ dòng tiêu đề

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
    text = "[📌] *Danh sách tài khoản sắp hết hạn:*
"
    for acc in accounts:
        text += f"\n• *{acc['nền tảng']}* | {acc['dịch vụ']}\n➡️ `{acc['account']}`\n📅 Đăng ký: {acc['date_reg']} | 💰 Giá: {acc['giá_bán']}\n"
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, parse_mode="Markdown")

async def on_demand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = extract_expiring_accounts()
    if not accounts:
        await update.message.reply_text("✅ Không có tài khoản nào sắp hết hạn.")
        return
    text = "[📌] *Danh sách tài khoản sắp hết hạn:*
"
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

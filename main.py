import os
import json
import datetime
import logging
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_CHAT_ID = os.getenv("CHANNEL_CHAT_ID")

SHEET_NAME = 'chatgpt'
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def connect_sheet():
    credentials_raw = os.getenv("GOOGLE_CREDENTIALS")
    if not credentials_raw:
        raise ValueError("Thiếu GOOGLE_CREDENTIALS")
    credentials_json = json.loads(credentials_raw)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_json, SCOPE)
    client = gspread.authorize(creds)
    return client.open_by_url("https://docs.google.com/spreadsheets/d/1ECU9jLUHFeAqpH5UggdFjkiEeiqc6F_ZHGD9Rs8Gc/edit").worksheet("chatgpt")

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

    today = datetime.now().strftime("%d/%m/%Y")
    text = f"📅 *NHẮC HẠN NGÀY {today}*\n🔔 Những tài khoản sắp hết hạn:\n\n"

    for acc in accounts:
        text += (
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 *Nền tảng:* {acc['nền tảng']}\n"
            f"🛠️ Dịch vụ: {acc['dịch vụ']}\n"
            f"👤 Tài khoản: `{acc['account']}`\n"
            f"📆 Đăng ký: {acc['date_reg']}\n"
            f"💰 Giá bán: {acc['giá_bán']}\n"
        )

    await context.bot.send_message(chat_id=CHANNEL_CHAT_ID, text=text, parse_mode="Markdown")

async def on_demand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = extract_expiring_accounts()
    if not accounts:
        await update.message.reply_text("✅ Không có tài khoản nào sắp hết hạn.")
        return
    today = datetime.now().strftime("%d/%m/%Y")
    text = f"📅 *NHẮC HẠN NGÀY {today}*\n🔔 Những tài khoản sắp hết hạn:\n\n"
    for acc in accounts:
        text += (
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 *Nền tảng:* {acc['nền tảng']}\n"
            f"🛠️ Dịch vụ: {acc['dịch vụ']}\n"
            f"👤 Tài khoản: `{acc['account']}`\n"
            f"📆 Đăng ký: {acc['date_reg']}\n"
            f"💰 Giá bán: {acc['giá_bán']}\n"
        )
    await update.message.reply_text(text, parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("hethan", on_demand))

    hour = int(os.getenv("REMIND_HOUR", "8"))
    minute = int(os.getenv("REMIND_MINUTE", "0"))
    from datetime import time
    app.job_queue.run_daily(notify_expiring, time=time(hour=hour, minute=minute))
    
    from telegram.ext import MessageHandler, filters

    async def reply_to_any_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🤖 Mình là bot nhắc hạn. Gửi /hethan để xem tài khoản sắp hết hạn nhé!")

    import asyncio
    from datetime import time

    async def main_async():
        app.add_handler(CommandHandler("hethan", on_demand))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_to_any_message))
        hour = int(os.getenv("REMIND_HOUR", "8"))
        minute = int(os.getenv("REMIND_MINUTE", "0"))
        app.job_queue.run_daily(notify_expiring, time=time(hour=hour, minute=minute))
        await app.initialize()
        await app.bot.set_webhook(url=os.getenv("WEBHOOK_URL") + "/webhook")
        await app.start()
        await app.run_webhook(
            listen="0.0.0.0",
            port=int(os.getenv("PORT", 8080)),
            url_path="webhook"
        )

    asyncio.run(main_async())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()

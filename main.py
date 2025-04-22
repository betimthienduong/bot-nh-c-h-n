import asyncio
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from utils import get_expiring_accounts
from datetime import time as dtime
import httpx

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
RAILWAY_URL = os.getenv("RAILWAY_URL")
PORT = int(os.getenv("PORT", 8443))

logging.basicConfig(level=logging.INFO)

def format_message(accounts):
    if not accounts:
        return "✅ Không có tài khoản nào sắp hết hạn."

    text = "[📌] *Danh sách tài khoản sắp hết hạn:*\n"
    for acc in accounts:
        text += f"""📱 {acc['platform']}
👤 {acc['account']}
🗓️ Reg: {acc['date_reg']} | 💰 Giá: {acc['Giá bán']}
⏰ Exp: {acc['exp_date']} (Còn {acc['remaining']} ngày)

"""
    return text.strip()

async def notify_expiring(context: ContextTypes.DEFAULT_TYPE):
    accounts = get_expiring_accounts()
    message = format_message(accounts)
    await context.bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode="Markdown")

async def hethan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = get_expiring_accounts()
    message = format_message(accounts)
    await update.message.reply_text(message, parse_mode="Markdown")

async def default_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Gửi /hethan để xem tài khoản sắp hết hạn nha!")

async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("hethan", hethan_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, default_response))
    app.job_queue.run_daily(notify_expiring, time=dtime(hour=8, minute=0))

    await app.initialize()
    await app.start()

    webhook_url = f"{RAILWAY_URL}/{TOKEN}"
    print("👉 Đang set webhook:", webhook_url)

    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"https://api.telegram.org/bot{TOKEN}/setWebhook",
            params={"url": webhook_url}
        )
        print("🔍 Telegram webhook response:", res.status_code, res.text)

    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=webhook_url
    )

    await app.updater.idle()

if __name__ == "__main__":
    asyncio.run(main())

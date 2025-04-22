
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from utils import get_expiring_accounts
from datetime import time as dtime
import os

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

logging.basicConfig(level=logging.INFO)

def format_message(accounts):
    if not accounts:
        return "✅ Không có tài khoản nào sắp hết hạn!"
    
    msg = "[📌] *Danh sách tài khoản sắp hết hạn:*
"
    for acc in accounts:
        msg += f"""
📱 {acc['platform']}
👤 {acc['account']}
🗓️ Reg: {acc['date_reg']} | 💰 Giá: {acc['price']}
⏰ Exp: {acc['exp_date']} (Còn {acc['remaining']} ngày)
"""
    return msg.strip()

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

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

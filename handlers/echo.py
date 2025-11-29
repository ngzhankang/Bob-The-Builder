from telegram import Update
from telegram.ext import ContextTypes

# makes tele bot echo what you typed and sent
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=update.message.text)
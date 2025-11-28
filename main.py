import os
from dotenv import load_dotenv
import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

# load telebot sercret api key and set in os env
load_dotenv()
API_KEY = os.getenv("TG_BOT_API_TOKEN")

# for logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I'm a bot, please talk to me!"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=update.message.text)
    

if __name__ == '__main__':
    application = ApplicationBuilder().token(API_KEY).build()
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)

    application.run_polling()
# IMPORTS

# logging
import logging

# telegram
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, CallbackQueryHandler

# ./config.py
from config import TELE_API_KEY

# ./handlers
from handlers import start, build_profile_conversation, build_food_search_conversation
from handlers.profile import profile_button


# CONFIG

# logging
logging.basicConfig(
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level = logging.INFO
)   


# TELEGRAM BOT

def main():

    # initialise telegram bot
    application = ApplicationBuilder().token(TELE_API_KEY).build()

    # bot command handlers
    application.add_handler(CommandHandler('start', start))   # /start handler
    application.add_handler(build_profile_conversation())     # /profile handler
    application.add_handler(build_food_search_conversation()) # /info handler
    # application.add_handler(CallbackQueryHandler(profile_button, pattern="^profile$"))

    print('Bot is running...')
    application.run_polling(poll_interval=3.0)


if __name__ == '__main__': main()
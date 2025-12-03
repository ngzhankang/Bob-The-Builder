import logging
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import TELE_API_KEY

from handlers import start, profile_handlers, menu_handlers, show_main_menu

# from handlers.menu import build_main_menu_conversation

# logging module config
logging.basicConfig(
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level = logging.INFO
)   

def main():
    # initialise telegram bot
    application = ApplicationBuilder().token(TELE_API_KEY).build()
    application.add_handler(CommandHandler('start', start)) # /start handler
    # application.add_handler(CommandHandler('menu', menu))   # /menu handler
    application.add_handler(profile_handlers())   # /profile handler

    for handler in menu_handlers():
        application.add_handler(handler)
    # application.add_handler(build_main_menu_conversation) # manages main menu convesations

    print('Bot is running...')
    application.run_polling(poll_interval=3.0)


if __name__ == '__main__':
    main()
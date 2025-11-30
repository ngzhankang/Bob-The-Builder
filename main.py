import logging
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import TELE_API_KEY

from handlers import start, build_profile_conversation
from handlers.profile import profile_button

# logging module config
logging.basicConfig(
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level = logging.INFO
)   

def main():
    # initialise telegram bot
    application = ApplicationBuilder().token(TELE_API_KEY).build()
    application.add_handler(CommandHandler('start', start)) # /start handler
    application.add_handler(build_profile_conversation())   # /profile handler
    # application.add_handler(CallbackQueryHandler(profile_button, pattern="^profile$"))

    print('Bot is running...')
    application.run_polling(poll_interval=3.0)


if __name__ == '__main__':
    main()
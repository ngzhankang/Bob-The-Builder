# standard library imports
import logging

# third-party imports
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler

# local imports
from config import TELE_API_KEY
from handlers import start, build_profile_conversation


# logging module config
logging.basicConfig(

    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level = logging.INFO

)   


def main():

    # initialise telegram bot
    application = ApplicationBuilder().token(TELE_API_KEY).build()

    start_handler = CommandHandler('start', start)
    profile_handler = build_profile_conversation()
    # echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    application.add_handler(start_handler)
    application.add_handler(profile_handler)
    # application.add_handler(echo_handler)

    print('Bot is running...')
    application.run_polling(poll_interval=3.0)


if __name__ == '__main__':
    
    main()
import logging
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler
from config import TELE_API_KEY

from handlers import start, echo


# for logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)   

def main():
    application = ApplicationBuilder().token(TELE_API_KEY).build()
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)

    print('Bot is running...')
    application.run_polling(poll_interval=3.0)

if __name__ == '__main__':
    main()
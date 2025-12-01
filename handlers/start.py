# /start
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from storeUserData import GetUserProfile

# start message for first timer clickers in the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id=update.effective_user.id
    existing=GetUserProfile(user_id)

    # inline button for /profile
    keyboard = [
        ["/profile setup!🌹"]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    # if the profile exists
    if existing:
        name = existing.get("NAME") or update.effective_user.first_name
        await update.message.reply_text(
            f"Welcome back, {name}! 👋\n\n"
            "Don't worry, i still have your nutrition profile saved! 😃\n\n"
            "Just to be sure, I need you to double check again before we proceed! ♥️",
            reply_markup=markup,
        )
    else:
        # creates a new one if new user
        await update.message.reply_text(
            "Hello and thank you for using preachTheBot! ♥️\n\n"
            "If youre here to potentially lose weight, gain muscle, or figure how to eat healthier, you are at the right place! But first lets get start with your nutrition profile! 💫\n\n"
            "Please press /profile to set up your profile!",
            reply_markup=markup,
        )
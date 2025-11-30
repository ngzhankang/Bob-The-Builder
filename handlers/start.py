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
        ["/profile"]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    # if the profile exists
    if existing:
        name = existing.get("NAME") or update.effective_user.first_name
        await update.message.reply_text(
            f"welcome back, {name}! 👋\n\n"
            "dont worry, i still have your nutrition profile saved!😃\n\n"
            "BUT just to be sureee, i need you to double check again before we proceed! welcome back again anyws! ♥️",
            reply_markup=markup,
        )
    else:
        # creates a new one if new user
        await update.message.reply_text(
            "♥️♥️♥️hey there and really thankeww for using me!!!\n\n"
            "🤖🤖🤖if youre here to potentially lose weight, gain muscle, or figure how to eat healthier, you asking the right bot! but first lets get start with your nutrition profile!\n\n"
            "let's setup your profile first - please press /profile to set up your profile!",
            reply_markup=markup,
        )
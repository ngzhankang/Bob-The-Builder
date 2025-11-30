# /start
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from storeUserData import GetUserProfile

# NAME, AGE, SEX, HEIGHT, WEIGHT, GOAL, ACTIVITY__LEVEL, DIET_STYLE, ALLERGIES, MISINFORMATION

# start message for first timer clickers in the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id=update.effective_user.id
    profile=GetUserProfile(user_id)

    # if the profile exists
    if profile:
        name = profile.get("NAME") or update.effective_user.first_name
        await update.message.reply_text(
            f"welcome back, {name}! 👋\n\n"
            "dont worry, i still have your nutrition profile saved!😃"
            "BUT just to be sureee, i need you to double check again before we proceed! welcome back again anyws! ♥️"
        )
        return ConversationHandler.END

    # creates a new one if new
    await update.message.reply_text(
        "hey there and really thankeww for using me♥️(im preacherTheBot incase you miss it!)\n\n"
        "before we get started, i need to check if we chat before(or in the past). if we did, welcome back!\n"
        "if you didnt, then maybe tell me more about yourself first! and then ill ask some rapid fire questions😈😈😈"
    )
    return ConversationHandler.END
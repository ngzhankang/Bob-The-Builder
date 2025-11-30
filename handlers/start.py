# /start
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from storeUserData import GetUserProfile

from handlers.profile import profile as profile_entry

# start message for first timer clickers in the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id=update.effective_user.id
    existing=GetUserProfile(user_id)

    # if the profile exists
    if existing:
        name = existing.get("NAME") or update.effective_user.first_name
        await update.message.reply_text(
            f"welcome back, {name}! 👋\n\n"
            "dont worry, i still have your nutrition profile saved!😃\n\n"
            "BUT just to be sureee, i need you to double check again before we proceed! welcome back again anyws! ♥️"
        )
        return ConversationHandler.END

    # creates a new one if new
    await update.message.reply_text(
        "♥️♥️♥️hey there and really thankeww for using me!!!\n\n"
        "🤖🤖🤖if youre here to potentially lose weight, gain muscle, or figure how to eat healthier, you asking the right bot! but first lets get start with your nutrition profile!\n\n"
        # "😈😈😈if you didnt, then maybe tell me more about yourself first! and then ill ask some rapid fire questions"
    )
    return await profile_entry(update, context)
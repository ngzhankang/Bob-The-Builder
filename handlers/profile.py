# for users to setup profiles
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters
from storeUserData import SaveUserProfile, GetUserProfile, DeleteUserProfile

# declare params
NAME, AGE, SEX, HEIGHT, WEIGHT, GOAL, ACTIVITY_LEVEL, DIET_STYLE, ALLERGIES, MISINFORMATION = range(10)

# fixed option for user to choose in telebot
SEX_OPTIONS = ["male", "female"]
ACTIVITY_OPTIONS = ["sedentary", "light", "moderate", "active", "very active"]
GOAL_OPTIONS = ["fat loss", "muscle gain", "better energy", "general health"]
DIET_OPTIONS = ["no preference", "vegetarian", "vegan", "low-carb", "halal"]

#  start profile (or update name)
async def profile_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    existing = GetUserProfile(user_id)

    if existing:
        name = existing.get("NAME") or update.effective_user.first_name
        await update.message.reply_text(
            f"uh ohh seems like you alr got a profile liao, {name} \n\n"
            "if you want to overwrite it, we needa go through the questions again to see if we are still in sync!\n"
            "if you want to delete your saved details completely, you can use the /deleteprofile command later...(although we dont want you to go)"
        )
    
    await update.message.reply_text(
        "let's set uppp your nutrition profile before we begin!\n\n"
        "how would you like me to call you? (no problem if you dont want me to know your real name, we good!)"
    )
    return NAME

# ask for age
async def ask_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["NAME"] = update.message.text.strip()
    await update.message.reply_text(
        "nice! how old are you (NUMBERS ONLY GRR)"
    )
    return AGE

# ask for sex
async def ask_sex(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # check age first
    try:
        age = int(update.message.text.strip())
        if not (1 <= age <= 120):
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            "that age looks abit wrong...please enter a valid age as a number"
        )
        return AGE
    
    # k now ask for sex
    context.user_data["AGE"] = age
    await update.message.reply_text(
        "whats your gender"
    )
    reply_markup = ReplyKeyboardMarkup(SEX_OPTIONS, one_time_keyboard=True, resize_keyboard=True)
    return SEX

# ask for height
async def ask_height(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["SEX"] = update.message.text.strip()
    await update.message.reply_text(
        "whats your height in cm? (e.g. 170)",
        reply_markup=ReplyKeyboardRemove(),
    )
    return HEIGHT

# ask for weight
async def ask_weight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        height = float(update.message.text.strip())
        if not (100 <= height <= 230):
            raise ValueError
    except ValueError:
        await update.message.reply_text("please enter a realistic height in cm, e.g. 170.")
        return HEIGHT

    context.user_data["HEIGHT"] = height
    await update.message.reply_text("what is your weight in kg? (e.g. 65.5)")
    return WEIGHT

# ask for the current goal
async def ask_goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        weight = float(update.message.text.strip())
        if not (30 <= weight <= 300):
            raise ValueError
    except ValueError:
        await update.message.reply_text("please enter a realistic weight in kg, e.g. 65.5.")
        return WEIGHT

    context.user_data["WEIGHT"] = weight
    await update.message.reply_text(
        "What is your main goal right now?",
        reply_markup=ReplyKeyboardMarkup(GOAL_OPTIONS, one_time_keyboard=True, resize_keyboard=True),
    )
    return GOAL

# ask for how active the user is rn
async def ask_activity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["GOAL"] = update.message.text.strip()
    await update.message.reply_text(
        "how would you describe your typical activity level?",
        reply_markup=ReplyKeyboardMarkup(ACTIVITY_OPTIONS, one_time_keyboard=True, resize_keyboard=True),
    )
    return ACTIVITY_LEVEL

# ask for diet style
async def ask_diet_style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["ACTIVITY_LEVEL"] = update.message.text.strip()
    await update.message.reply_text(
        "do you follow any particular diet style?",
        reply_markup=ReplyKeyboardMarkup(DIET_OPTIONS, one_time_keyboard=True, resize_keyboard=True),
    )
    return DIET_STYLE

# ask for allergies
async def ask_allergies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["DIET_STYLE"] = update.message.text.strip()
    await update.message.reply_text(
        "any food allergies or ingredients you must avoid? "
        "(e.g. peanuts, shellfish, lactose; type 'none' if no allergies.)",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ALLERGIES

# ask for the misinformation

async def ask_misinformation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["ALLERGIES"] = update.message.text.strip()
    await update.message.reply_text(
        "lastly, what diet myths or nutrition claims have you seen online that "
        "you're unsure about? You can list a few, or type 'none'."
    )
    return MISINFORMATION

# once we gather all the basic info, save it in first

async def profile_finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["MISINFORMATION"] = update.message.text.strip()

    user_id = update.effective_user.id
    profile = {
        "NAME": context.user_data["NAME"],
        "AGE": context.user_data["AGE"],
        "SEX": context.user_data["SEX"],
        "HEIGHT": context.user_data["HEIGHT"],
        "WEIGHT": context.user_data["WEIGHT"],
        "GOAL": context.user_data["GOAL"],
        "ACTIVITY_LEVEL": context.user_data["ACTIVITY_LEVEL"],
        "DIET_STYLE": context.user_data["DIET_STYLE"],
        "ALLERGIES": context.user_data["ALLERGIES"],
        "MISINFORMATION": context.user_data["MISINFORMATION"],
    }
    SaveUserProfile(user_id, profile)

    # once successful, assure user that i got this
    await update.message.reply_text(
        "Thanks! Your nutrition profile is saved ✅\n\n"
        "From now on, I’ll use this info to:\n"
        "• Give clearer, more relevant nutrition guidance for your goals.\n"
        "• Suggest practical food swaps that fit your diet style and allergies.\n"
        "• Help you fact-check the myths you mentioned.\n\n"
        "You can update this anytime with /profile."
    )
    return ConversationHandler.END

async def profile_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # to show the current data of the user
    user_id = update.effective_user.id
    profile = GetUserProfile(user_id)
    if not profile:
        await update.message.reply_text(
            "seems like you haven't set up your profile yet ~ please press /profile to setup" 
        )
        return
    
    text = (
        f"Here’s your current nutrition profile:\n\n"
        f"Name: {profile['NAME']}\n"
        f"Age: {profile['AGE']}\n"
        f"Sex: {profile['SEX']}\n"
        f"Height: {profile['HEIGHT']} cm\n"
        f"Weight: {profile['WEIGHT']} kg\n"
        f"Goal: {profile['GOAL']}\n"
        f"Activity level: {profile['ACTIVITY_LEVEL']}\n"
        f"Diet style: {profile['DIET_STYLE']}\n"
        f"Allergies: {profile['ALLERGIES']}\n"
        f"Myths you mentioned: {profile['MISINFORMATION']}"
    )
    await update.message.reply_text(text)

async def profile_delete_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    DeleteUserProfile(user_id)
    await update.message.reply_text(
        "your saved profile has been deleted. You can create a new one anytime with /profile."
    )

async def profile_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Profile setup cancelled. Your previous data is unchanged.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


def get_profile_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points
    )
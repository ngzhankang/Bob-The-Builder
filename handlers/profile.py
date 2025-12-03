# for users to setup profiles
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters
from storeUserData import SaveUserProfile, GetUserProfile, DeleteUserProfile
from handlers.states import *

# fixed option for user to choose in telebot (has to be list of list)
# see docs https://docs.python-telegram-bot.org/en/stable/telegram.replykeyboardmarkup.html#telegram.ReplyKeyboardMarkup.params.keyboard
SEX_OPTIONS = [["male", "female"]]
ACTIVITY_OPTIONS = [["sedentary", "light"], ["moderate", "active", "very active"]]
GOAL_OPTIONS = [["fat loss", "muscle gain"], ["better energy", "general health"]]
DIET_OPTIONS = [["no preference", "vegetarian"], ["vegan", "low-carb", "halal"]]
SLUMP_CHECK_OPTIONS = [["yes", "no"]]
MORNING_KICK_OPTIONS = [["groggy", "ready to go", "hungry"]]

# profile setup. acts like a state machine
def profile_handlers():
    from handlers import universal_cancel
    return ConversationHandler(
        entry_points=[
            CommandHandler("profile", profile)
            ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_age)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_sex)],
            SEX: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_height)],
            HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_weight)],
            WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_goal)],
            GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_activity)],
            ACTIVITY_LEVEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_diet_style)],
            DIET_STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_allergies)],
            ALLERGIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_slump_check)],
            SLUMP_CHECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_morning_kick)],
            MORNING_KICK: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_hydration_check)],
            HYDRATION_CHECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_finish)],
            # MAIN_MENU:  [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_selection)],
            AWAITING_EDIT_CONFIRMATION:  [MessageHandler(filters.TEXT & filters.COMMAND, await_edit_confirmation)]
        },
        fallbacks=[CommandHandler("cancel", universal_cancel)]
    )

# upon trigger from the /profile button in start for new users
async def profile_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query.data == "profile":
        # call the /profile flow entry
        await profile(update, context)

#  start profile (or update name)
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # to detect if it comes from the button or from typing /profile
    if update.message:
        msg = update.message
        user = update.effective_user
    else:
        query = update.callback_query
        await query.answer()
        msg = query.message
        user = query.from_user

    user_id = user.id
    existing = GetUserProfile(user_id)

    if existing:
        name = existing.get("NAME") or user.first_name
        await msg.reply_text(
            f"Seems like you have an existing profile, {name}! \n\n"
            f"Your details:\n"
            f"Age: {existing.get('AGE')}\n"
            f"Sex: {existing.get('SEX')}\n"
            f"Height: {existing.get('HEIGHT')}\n"
            f"Weight: {existing.get('WEIGHT')}\n"
            f"Goal: {existing.get('GOAL')}\n"
            f"Activity Level: {existing.get('ACTIVITY_LEVEL')}\n"
            f"Diet Style: {existing.get('DIET_STYLE')}\n"
            f"Allergies: {existing.get('ALLERGIES')}\n\n"
            "If you want to overwrite it, click on the /edit command!\n\n"
            "If you accidentally pressed edit, you can use the /cancel command.\n\n"
            "If you want to delete your saved details completely, you can use the /deleteprofile command.",
            reply_markup=ReplyKeyboardMarkup([["/edit ✔️", "/cancel ❌"]], one_time_keyboard=True, resize_keyboard=True)
        )
        return AWAITING_EDIT_CONFIRMATION
    
    else:
        await msg.reply_text("How would you like me to call you?")
        return NAME
    
# function to check if user really wants to edit profile
async def await_edit_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip().lower()
    if "/edit" in text:
        await update.message.reply_text("How would you like me to call you?")
        return NAME
    else:
        from handlers.menu import show_main_menu
        await show_main_menu(update, context)
        return ConversationHandler.END

# ask for age
async def ask_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["NAME"] = update.message.text.strip()
    await update.message.reply_text(
        "And what is your age?"
    )
    return AGE

# ask for sex
async def ask_sex(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # check age first
    try:
        age = int(update.message.text.strip())
        if not (1 <= age <= 100):
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            "That age looks a bit wrong...please enter a valid age as a number"
        )
        return AGE
    
    # k now ask for sex
    context.user_data["AGE"] = age
    reply_markup = ReplyKeyboardMarkup(SEX_OPTIONS, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "What is your gender?\n\nAge and gender significantly impact how your body uses energy. ⚡",
        reply_markup=reply_markup
    )
    return SEX

# ask for height
async def ask_height(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # check gender in case user types random 
    try:
        sex = str(update.message.text.strip())
        if sex not in SEX_OPTIONS[0]:
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            "Please choose a valid option"
        )
        return SEX
    
    context.user_data["SEX"] = update.message.text.strip()
    await update.message.reply_text(
        "What is your height in cm? (e.g. 170)",
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
        await update.message.reply_text("Please enter a realistic height in cm, e.g. 170.")
        return HEIGHT

    context.user_data["HEIGHT"] = height
    await update.message.reply_text(
        "What is your weight in kg? (e.g. 65.5)\n\nHeight and weight are used to calculate your baseline energy needs. ⚡"
        )
    return WEIGHT

# ask for the current goal
async def ask_goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        weight = float(update.message.text.strip())
        if not (30 <= weight <= 300):
            raise ValueError
    except ValueError:
        await update.message.reply_text("Please enter a realistic weight in kg, e.g. 65.5.")
        return WEIGHT

    context.user_data["WEIGHT"] = weight
    await update.message.reply_text(
        "To give you the best advice, what's your main health focus right now?",
        reply_markup=ReplyKeyboardMarkup(GOAL_OPTIONS, one_time_keyboard=True, resize_keyboard=True),
    )
    return GOAL

# ask for how active the user is rn
async def ask_activity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # check goal in case user types random 
    try:
        goal = update.message.text.strip()
        if goal not in GOAL_OPTIONS[0] and goal not in GOAL_OPTIONS[1]:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Please choose a valid option")
        return GOAL
    
    context.user_data["GOAL"] = goal
    await update.message.reply_text(
        "How active are you on an average week?",
        reply_markup=ReplyKeyboardMarkup(ACTIVITY_OPTIONS, one_time_keyboard=True, resize_keyboard=True),
    )
    return ACTIVITY_LEVEL

# ask for diet style
async def ask_diet_style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # check activity level in case user types random 
    try:
        activity = update.message.text.strip()
        if activity not in ACTIVITY_OPTIONS[0] and activity not in ACTIVITY_OPTIONS[1]:
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            "Please choose a valid option"
        )
        return ACTIVITY_LEVEL
    
    context.user_data["ACTIVITY_LEVEL"] = update.message.text.strip()
    await update.message.reply_text(
        "Before I suggest a recipe in future, do you follow any specific diet, like vegetarian or keto? I want to make sure the ingredients work for you!",
        reply_markup=ReplyKeyboardMarkup(DIET_OPTIONS, one_time_keyboard=True, resize_keyboard=True),
    )
    return DIET_STYLE

# ask for allergies
async def ask_allergies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # check diet level in case user types random 
    try:
        diet = update.message.text.strip()
        if diet not in DIET_OPTIONS[0] and diet not in DIET_OPTIONS[1]:
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            "Please choose a valid option"
        )
        return DIET_STYLE
    
    context.user_data["DIET_STYLE"] = update.message.text.strip()
    await update.message.reply_text(
        "For safety first, do you have any food allergies or intolerances I need to watch out for?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ALLERGIES

# ask for slump check
async def ask_slump_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["ALLERGIES"] = update.message.text.strip()
    reply_markup = ReplyKeyboardMarkup(SLUMP_CHECK_OPTIONS, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Do you often feel a 'crash' or low energy in the mid-afternoon (around 2-4PM)?\n\nThis could be an indicator of blood sugar spikes/crashes from high-sugar lunches.",
        reply_markup=reply_markup
    )
    return SLUMP_CHECK

# ask for morning kick
async def ask_morning_kick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # check slump check
    try:
        slump_check = str(update.message.text.strip())
        if slump_check not in SLUMP_CHECK_OPTIONS[0]:
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            "Please choose a valid option"
        )
        return SLUMP_CHECK
    
    context.user_data["SLUMP_CHECK"] = update.message.text.strip()
    reply_markup = ReplyKeyboardMarkup(MORNING_KICK_OPTIONS, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "How do you feel when you wake up?\n\nThis could get me to better know your sleep quality or late-night-eating habits.",
        reply_markup=reply_markup
    )
    return MORNING_KICK

# ask for hydration
async def ask_hydration_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # check morning kick
    try:
        morning_kick = str(update.message.text.strip())
        if morning_kick not in MORNING_KICK_OPTIONS[0]:
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            "Please choose a valid option"
        )
        return MORNING_KICK
    
    context.user_data["MORNING_KICK"] = update.message.text.strip()
    await update.message.reply_text(
        "Be honest - how much plain water do you drink a day? (In litres)"
    )
    return HYDRATION_CHECK

# once we gather all the basic info, save it in first
async def profile_finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # check if water consumption is based
    try:
        hydration = float(update.message.text.strip())
        if not (0 <= hydration <= 6):
            raise ValueError
    except ValueError:
        await update.message.reply_text("Please enter a realistic water consumption volume in litres, e.g. 3.3\n\nDid you know that dehydration is the #1 silent cause of fatigue?")
        return HYDRATION_CHECK

    context.user_data["HYDRATION_CHECK"] = hydration

    # calculate basal metabolic rate using Mifflin St-Jeor Equation
    # see https://reference.medscape.com/calculator/846/mifflin-st-jeor-equation
    if context.user_data["SEX"].lower() == "male":
        bmr = (10*context.user_data["WEIGHT"]) +(6.25*context.user_data["HEIGHT"]) - (5*context.user_data["AGE"]) + 5
    else:
        bmr = (10*context.user_data["WEIGHT"]) +(6.25*context.user_data["HEIGHT"]) - (5*context.user_data["AGE"]) - 161

    # calculate total Daily Energy Expenditure
    # see https://www.healthhub.sg/well-being-and-lifestyle/personal-care/healthy-weight-loss
    # https://reference.medscape.com/calculator/846/mifflin-st-jeor-equation#
    if context.user_data["ACTIVITY_LEVEL"] == 'sedentary':
        tdee = bmr*1.2
    elif context.user_data["ACTIVITY_LEVEL"] == 'light':
        tdee = bmr*1.375
    elif context.user_data["ACTIVITY_LEVEL"] == 'moderate' or context.user_data["ACTIVITY_LEVEL"] == 'active':
        tdee = bmr*1.55
    else:
        tdee = bmr*1.725

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
        "SLUMP_CHECK": context.user_data["SLUMP_CHECK"],
        "MORNING_KICK": context.user_data["MORNING_KICK"],
        "HYDRATION_CHECK": context.user_data["HYDRATION_CHECK"],
        "BMR": bmr,
        "TDEE": tdee,
    }
    SaveUserProfile(user_id, profile)

    # once successful, assure user that i got this
    from handlers.menu import show_main_menu, menu_keyboard
    await update.message.reply_text(
        "Thanks! Your nutrition profile is saved ✅\n\n"
        "From now on, I’ll use this info to:\n"
        "• Give clearer, more relevant nutrition guidance for your goals.\n"
        "• Suggest practical food swaps that fit your diet style and allergies.\n"
        "• Help you fact-check the myths you mentioned.\n\n"
        "You can update this anytime with /profile."
    )
    await show_main_menu(update, context)
    return MAIN_MENU

# display the current details of the user upon request
async def profile_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # to show the current data of the user
    user_id = update.effective_user.id
    profile = GetUserProfile(user_id)
    if not profile:
        await update.message.reply_text(
            "Seems like you haven't set up your profile yet ~ please press /profile to setup" 
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

# delete the profile upon request
async def profile_delete_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    DeleteUserProfile(user_id)
    await update.message.reply_text(
        "your saved profile has been deleted. You can create a new one anytime with /profile."
    )
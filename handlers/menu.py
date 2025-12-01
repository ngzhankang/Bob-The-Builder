# file to manage menu after successful user enrollment
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters

# acts like a state machine to determine where it is right now
STAGES = {
    "ONBOARDING_GOAL": 0,
    "ONBOARDING_STATS": 1,
    "ONBOARDING_ENERGY": 2,
    "MAIN_MENU": 3
}

# menu buttons for the main landing page
MENU_BUTTONS = [
    ["🥗 What should I eat?"],
    ["⚡ Fix my Energy"],
    ["🔍 Fact Check Trend"],
    ["👤 My Stats"]
]

menu_keyboard = ReplyKeyboardMarkup(MENU_BUTTONS, one_time_keyboard=True, resize_keyboard=True)

# implementing the /menu handle
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome to the main menu. Please choose an option:",
        reply_markup=menu_keyboard
    )

# implements checksum on functions to trigger upon button input
async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if text == "🥗 What should I eat?":
        await suggest_meal(update, context)
    elif text == "⚡ Fix my Energy":
        await fix_energy(update, context)
    elif text == "🔍 Fact Check Trend":
        await fact_check_trend(update, context)
    elif text == "👤 My Stats":
        await show_stats(update, context)
    else:
        await update.message.reply_text("Sorry, I didn't understand that. Please select an option from the menu.")

# give suggestions to user what meal he/she can possibly eat
async def suggest_meal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: implement TDEE + time of day meal suggestions
    await update.message.reply_text("This will suggest meals based on your TDEE and time of day.")

# informs user his/her energy level now and what he/she can eat
async def fix_energy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: implement energy crisis diagnosis and snack recommendation
    await update.message.reply_text("This will offer energy-boosting advice tailored to you.")

# do fact checking for users
async def fact_check_trend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: ask for myth/link input and call Perplexity API
    await update.message.reply_text("Please send me the diet myth or link you'd like me to fact-check.")

# show the details of the user right now
async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: fetch user's BMR/TDEE from stored profile and display
    user_id = update.effective_user.id
    profile = GetUserProfile(user_id)
    if not profile:
        await update.message.reply_text("You haven't set up your profile yet. Use /profile to get started.")
        return
    bmr = profile.get("BASAL_METABOLIC_RATE", "N/A")
    tdee = profile.get("TDEE", "N/A")
    await update.message.reply_text(f"Your stats:\nBMR: {bmr} kcal/day\nTDEE: {tdee} kcal/day")

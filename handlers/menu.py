# file to manage menu after successful user enrollment
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters, ConversationHandler, CommandHandler
from storeUserData import GetUserProfile
from handlers.foodSearch import *
from handlers.states import *
from perplexityClient import run_fact_check_pipeline

# menu buttons for the main landing page
MENU_BUTTONS = [
    ["🥗 What should I eat?", "⚡ Fix my Energy"],
    ["🔍 Fact Check Trend", "👤 My Stats"],
    ["🧪 Nutritional Information"]
]

menu_keyboard = ReplyKeyboardMarkup(MENU_BUTTONS, one_time_keyboard=True, resize_keyboard=True)
cancel_keyboard = ReplyKeyboardMarkup([["/cancel ❌"]], one_time_keyboard=True, resize_keyboard=True)

# # use defined states inside conversationhandler
# def build_main_menu_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     return ConversationHandler(
#         entry_points=[
#             CommandHandler('menu', show_main_menu)],
#         states={
#             # WHAT_TO_EAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler)]
#             # FIX_ENERGY: [MessageHandler(filters.TEXT & ~filters.COMMAND, fix_energy)],
#             MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_selection)],
#             FACT_CHECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler)],
#         },
#         fallbacks=[CommandHandler('cancel', universal_cancel)]
#     )

# handles all buttons from menu and what to do next
def menu_handlers():
    return [
        MessageHandler(filters.Text("👤 My Stats"), show_stats),
        MessageHandler(filters.Text("🔍 Fact Check Trend"), fact_check_trend),
        MessageHandler(filters.TEXT & ~filters.COMMAND, fact_check_input),
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_selection)
    ]
    text = update.message.text

    # if text == "🥗 What should I eat?":
    #     await suggest_meal(update, context)
    # elif text == "⚡ Fix my Energy":
    #     await fix_energy(update, context)
    # elif text == "🔍 Fact Check Trend":
    #     await fact_check_trend(update, context)
    # elif text == "👤 My Stats":
    #     return await show_stats(update, context)
    # else:
    #     await update.message.reply_text("Sorry, I didn't understand that. Please select an option from the menu.")
    #     return MAIN_MENU

# implementing the /menu handle
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Welcome to the main menu. Please choose an option:",
        reply_markup=menu_keyboard
    )

# handles fact check inputs
async def fact_check_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_fact_check"):
        context.user_data["awaiting_fact_check"] = False
        claim = update.message.text
        trusted_sites = [
            "healthhub.sg", "moh.gov.sg", "cdc.gov", "thelancet.com",
            "healthxchange.sg", "skh.com.sg", "gleneagles.com.sg", "sgh.gov.sg", "hsa.gov.sg", "activesgcircle.gov.sg", "healthiersg.gov.sg",
            "nlb.gov.sg", "snda.org.sg", "asiaone.com", "todayonline.com", "kkh.com.sg", "rafflesmedicalgroup.com", "who.int", "nhs.uk", "cochrane.org",
            "harvard.edu", "nice.org.uk", "pubmed.ncbi.nlm.nih.gov", 'examine.com', 'nih.gov', 'sportsnutritionsociety.org', 'mayoclinic.org', 'mayoclinic.org'
        ]
        from perplexityClient import run_fact_check_pipeline
        await run_fact_check_pipeline(update, context, claim, trusted_sites, menu_keyboard)
        # await show_main_menu(update, context)
        # return MAIN_MENU
    else:
        return await handle_menu_selection(update, context)


# implements checksum on functions to trigger upon button input
async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text == "🥗 What should I eat?":
        await suggest_meal(update, context)
        return MAIN_MENU
    elif text == "⚡ Fix my Energy":
        await fix_energy(update, context)
        return MAIN_MENU
    elif text == "🔍 Fact Check Trend":
        await fact_check_trend(update, context)
        return MAIN_MENU
    elif text == "👤 My Stats":
        return await show_stats(update, context)
    elif text == "🧪 Nutritional Information":
        return await info(update, context)
    else:
        await update.message.reply_text("Sorry, I didn't understand that. Please select an option from the menu.")
        return MAIN_MENU

# give suggestions to user what meal he/she can possibly eat
async def suggest_meal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: implement TDEE + time of day meal suggestions
    # 1. get calculated tdee
    # 2. get current time from telegram
    # 3. construct prompt for perplexity
    await update.message.reply_text("This will suggest meals based on your TDEE and time of day.")

# informs user his/her energy level now and what he/she can eat
async def fix_energy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO: implement energy crisis diagnosis and snack recommendation
    # 
    await update.message.reply_text("This will offer energy-boosting advice tailored to you.")

# do fact checking for users
async def fact_check_trend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_fact_check"] = True
    await update.message.reply_text(
        "Please send me the diet myth or link you'd like me to fact-check.")
    # return FACT_CHECK

# show the details of the user right now. all details
async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    profile = GetUserProfile(user_id)
    if not profile:
        await update.message.reply_text("You haven't set up your profile yet. Use /profile to get started.")
        return MAIN_MENU
    stats_line = [f"{key.replace('_', ' ').title()}: {value}" for key, value in profile.items()]
    stats_text = "Your full profile details:\n\n" + "\n".join(stats_line)
    await update.message.reply_text(stats_text)
    
    # include the main menu after showing
    await update.message.reply_text(
        "Back to main menu. Please choose an option:",
        reply_markup=menu_keyboard
    )
    # return MAIN_MENU

# handler incase the anyone wants to leave setup/or any functions
async def universal_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # include the main menu after showing
    await update.message.reply_text(
        "Back to main menu. Please choose an option:",
        reply_markup=menu_keyboard
    )
    return MAIN_MENU
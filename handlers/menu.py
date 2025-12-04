# file to manage menu after successful user enrollment
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters, ConversationHandler, CommandHandler
from storeUserData import GetUserProfile
from handlers.states import *
from handlers.energy import diagnose_energy, get_user_snacks, calculate_meal_budget, get_meal_candidates
from perplexityClient import run_fact_check_pipeline, get_snack_recommendations, get_meal_recommendations

# menu buttons for the main landing page
MENU_BUTTONS = [
    ["🥗 What should I eat?", "⚡ Fix my Energy"],
    ["🔍 Fact Check Trend", "👤 My Stats"],
    ["🧪 Nutritional Information"]
]

menu_keyboard = ReplyKeyboardMarkup(MENU_BUTTONS, one_time_keyboard=True, resize_keyboard=True)
cancel_keyboard = ReplyKeyboardMarkup([["/cancel ❌"]], one_time_keyboard=True, resize_keyboard=True)

# handles all buttons from menu and what to do next
def menu_handlers():
    return [
        MessageHandler(filters.Text("👤 My Stats"), show_stats),
        MessageHandler(filters.Text("🔍 Fact Check Trend"), fact_check_trend),
        MessageHandler(filters.TEXT & ~filters.COMMAND, fact_check_input),
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_selection)
    ]
 
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
    # elif text == "🧪 Nutritional Information":
    #     return await info(update, context)
    else:
        await update.message.reply_text("Sorry, I didn't understand that. Please select an option from the menu.")
        return MAIN_MENU

# give suggestions to user what meal he/she can possibly eat
async def suggest_meal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    profile = GetUserProfile(user_id)

    if not profile:
        await update.message.reply_text("Please set up your profile first: /profile")
        return
    
    # Calculate meal context
    meal_context = calculate_meal_budget(profile)
    
    # Get HPB food candidates
    candidates = get_meal_candidates(profile, meal_context, meal_context["budget_kcal"])
    snack_list = "\n".join([f"- {c['name']} ({c['kcal']:.0f}kcal, {c['protein']:.1f}g protein)" for c in candidates])
    
    # Get Perplexity recommendation
    recommendation = await get_meal_recommendations(snack_list, profile, meal_context["meal_type"], meal_context["budget_kcal"])
    
    await update.message.reply_text(
        f"🍽️ **{meal_context['meal_type'].title()}** ({meal_context['budget_kcal']}kcal):\n\n"
        f"{recommendation}"
    )

    # include the main menu after showing
    await update.message.reply_text(
        "Back to main menu. Please choose an option:",
        reply_markup=menu_keyboard
    )

# informs user his/her energy level now and what he/she can eat
async def fix_energy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    profile = GetUserProfile(update.effective_user.id)

    if not profile:
        await update.message.reply_text("Please set up your profile with /profile first.")
        return

    issues = diagnose_energy(profile)

    if "underhydrated" in issues:
        await update.message.reply_text(
            "You're underhydrated. Aim for at least 1.5 - 2L water today."
        )

    if "afternoon_crash" in issues:
        user_snacks = get_user_snacks(profile)
        snack_list = "\n".join(f"- {s['name']} ({s['kcal']:.0f} kcal, {s['protein']:.1f} g protein)" for s in user_snacks)
        recommendations = await get_snack_recommendations(snack_list, profile)
        await update.message.reply_text(
            f"Your TDEE is {profile.get('TDEE', '?')} kcal. Here are some snack options for your 3 PM crash:\n\n{recommendations}"
        )
    
    if "poor_morning_energy" in issues:
        await update.message.reply_text("Groggy mornings? Try avoiding caffeine after 2 PM and heavy meals before bedtime.")

    if "needs_morning_fuel" in issues:
        await update.message.reply_text("Waking hungry? Have a protein-rich breakfast with fiber within one hour of waking.")

    if not issues:
        await update.message.reply_text("Your energy profile looks solid. Keep up the good habits!")
        
    # include the main menu after showing
    await update.message.reply_text(
        "Back to main menu. Please choose an option:",
        reply_markup=menu_keyboard
    )

# do fact checking for users
async def fact_check_trend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_fact_check"] = True
    await update.message.reply_text(
        "Please send me the diet myth or link you'd like me to fact-check.")

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
    return ConversationHandler.END
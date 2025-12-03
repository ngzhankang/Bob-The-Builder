# IMPORTS

# json
import json

# rapidfuzz
from rapidfuzz import process, fuzz

# re
from re import findall

# telegram
from telegram import Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

# ./handlers
from handlers.menu import *
from handlers.states import *


# FOOD DATA

# load food data
try:

    with open("./foodSearch/foodData.json", "r", encoding="utf-8") as f:

        food_data = json.load(f)

except:

    food_data = {}

# get list of food names
food_names = food_data.keys()


# CONVERSATION HANDLER

WAITING_QUERY, WAITING_SELECT = range(2)

def build_food_search_conversation() -> ConversationHandler:
    """Defines conversation entry points and states."""

    return ConversationHandler(
        allow_reentry=True,
        entry_points=[
            MessageHandler(filters.Regex("^🧪 Nutritional Information$") & ~filters.COMMAND, info),
            CommandHandler("info", info)
        ],
        fallbacks=[
            CommandHandler("cancel", cancel)
        ],
        states={
            WAITING_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_food)],
            WAITING_SELECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_nut_data)]
        }
    )

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point for getting nutritional data of food through /info command."""

    await update.message.reply_text(
        "What food's nutritional information would you like to search for?",
        reply_markup=None
    )
    return WAITING_QUERY

async def search_food(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shows food name matches from the user's query."""

    # get user query
    query = update.message.text.strip()

    # validate command arguments
    if not query:

        await update.message.reply_text(
            "Sorry, I didn't quite catch that! What food's nutritional information would you like to search for?",
        )
        return WAITING_QUERY

    # use fuzzy search to find top five likely matches
    matches = process.extract(query, food_names, scorer=fuzz.WRatio, limit=5)

    # only keep matches with scores above a threshold of 75.0
    matches = [match for match, score, _ in matches if score >= 75.0]

    # validate matches
    if not matches:

        await update.message.reply_text(
            f"Sorry, no nutritional information for  `{query}`  found!",
            parse_mode="MARKDOWN"
        )
        return ConversationHandler.END
    
    # store matches into context user data
    context.user_data["food_matches"] = matches

    # create list of matches
    msg = "Which food's nutritional information would you like to see?\n\n"
    for n, food_name in enumerate(matches, 1):

        msg += f"{n}.   _{food_name}_\n"
    
    await update.message.reply_text(msg, parse_mode="MARKDOWN")

    # update state to waiting on user to select
    return WAITING_SELECT

async def get_nut_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Validates user selection and queries nutritional information."""

    # get matches from context user data
    matches = context.user_data.get("food_matches", [])

    # validate user input
    try:

        # get index of selected match
        i = int(update.message.text.strip()) - 1

        # validate index
        if not (0 <= i < len(matches)): raise ValueError
    
    except ValueError:

        # give user feedback and maintain state
        await update.message.reply_text(
            f"Please reply with a number from 1 to {len(matches)} or  `/cancel`.",
            parse_mode="MARKDOWN"
        )
        return WAITING_SELECT

    # get nutritional data of food
    nut_data = food_data[matches[i]]["Nutritional Data"]

    # get serving size
    serving_size = food_data[matches[i]]["Default Serving Size"].split(" ")[-1]

    # add amount of each nutrient into message
    msg = f"*{matches[i].title()}*\n\n`{'Per':<17} 100{findall(r'[a-z]+', serving_size)[0]:<4} Serving`\n"
    for key, value in nut_data.items():

        # handle none values
        amounts = list(value.values())
        amounts = [amount if amount != None else "" for amount in amounts]

        msg += f"`{key:<17} {amounts[0]:<7} {amounts[1]}`\n"

    await update.message.reply_text(msg, parse_mode="MARKDOWN", reply_markup=menu_keyboard)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Exits conversation."""

    await update.message.reply_text(
            f"Cancelled. Use  `/info <food>`  if you'd like to search again!",
            parse_mode="MARKDOWN",
            reply_markup=menu_keyboard
        )
    return ConversationHandler.END
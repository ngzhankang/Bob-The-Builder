# handles responses from perplexity
from telegram import Update
from telegram.ext import CallbackContext
from perplexityClient import get_perplexity_response

async def handle_response(update: Update, content: CallbackContext) -> None:
    user_query = update.message.text
    chat_id = update.message.chat_id

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    aiResponse = await get_perplexity_response(user_query)

    await update.message.reply_text(aiResponse)
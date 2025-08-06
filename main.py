import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

import os
from dotenv import load_dotenv

import json

load_dotenv()

TOKEN = os.getenv("TOKEN")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

with open('user_info.json', 'r') as file:
    user_info = json.load(file)

with open('languages.json', 'r') as file:
    languages = json.load(file)

def get_translations(update, context) -> None:
    user_id = str(update.message.from_user['id'])
    language = user_info.get(user_id, "rus")
    return languages[language]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    translations = get_translations(update, context)

    """Sends a message with three inline buttons attached."""
    keyboard = [
        [
            InlineKeyboardButton(translations["buttons"]["search"], callback_data="search"),
        ],
        [
            InlineKeyboardButton(translations["buttons"]["annotation"], callback_data="annotation")
        ],
        [
            InlineKeyboardButton(translations["buttons"]["bibliography"], callback_data="bibliography")
        ],
        [
            InlineKeyboardButton(translations["buttons"]["plagiarism"], callback_data="plagiarism")
        ],
        [
            InlineKeyboardButton(translations["buttons"]["analyze"], callback_data="analyze")
        ],
        [
            InlineKeyboardButton(translations["buttons"]["offer"], callback_data="offer")
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(translations["buttons"]["popup"], reply_markup=reply_markup)

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("search")

async def handle_annotation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("annotation")

async def handle_bibliography(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("bibliography")
    
async def handle_plagiarism(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("plagiarism")

async def handle_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("analyze")

async def handle_offer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("offering")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()
    match query.data:
        case "search":
            await handle_search(update, context)
        case "annotation":
            await handle_annotation(update, context)
        case "bibliography":
            await handle_bibliography(update, context)
        case "plagiarism":
            await handle_plagiarism(update, context)
        case "analyze":
            await handle_analyze(update, context)
        case "offer":
            await handle_offer(update, context)

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    translations = get_translations(update, context)
    """Changes users ui language"""

    keyboard = [
        [
            InlineKeyboardButton("Русский", callback_data="lang_rus"),
        ],
        [
            InlineKeyboardButton("Қазақша", callback_data="lang_kaz")
        ],
        [
            InlineKeyboardButton("English", callback_data="lang_eng")
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(translations["language"]["popup"], reply_markup=reply_markup)

async def handle_change_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()
    user_id = str(update.effective_user.id)
    user_info[user_id] = query.data[-3:]
    with open('user_info.json', 'w') as file:
        json.dump(user_info, file, indent=4)
    translations = languages[query.data[-3:]]
    await query.edit_message_text(translations["language"]["done"])

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("language", change_language))
    application.add_handler(CallbackQueryHandler(handle_change_language, pattern = "^lang_"))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

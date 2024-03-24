from typing import Final
import logging
from datetime import datetime as dt
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
)
from bson.objectid import ObjectId
from mongo_client import ExpenseMongoClient

BOT_TOKEN : Final = "7079993461:AAGryn5WVrZlREgS8HwRYMpltQEQr7jKXPI"

dev_ids = [44557320]

# Enable Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# connect to your mongodb
db_client = ExpenseMongoClient("mongodb+srv://jigsaw1313:Aramis2427@expenses.0cbt6ew.mongodb.net/", 27017)

# Handlers
async def start_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello Mohammadreza, Let's record your daily expenses",
        reply_to_message_id=update.effective_message.id,
    )

HELP_COMMAND_RESPONSE = """
Greetings! Here are the commands you can use with this bot:

/start -> Begin interacting with the bot.
/add <amount> <category> <description> -> Add new expense.
/delete <document_id> -> Removes expense by document id.
/get_expenses -> Shows list of all expenses.
/get_categories -> Shows all categories.
/get_total -> Show total expenses recorded in database.
/get_total_by_category -> Shows total expenses for each category.
"""

async def help_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text = HELP_COMMAND_RESPONSE,
        reply_to_message_id=update.effective_message.id
    )


async def add_expense_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    amount = context.args[0]
    category = context.args[1]
    description = " ".join(context.args[2:])

    # Call the add_expense method on the instance
    db_client.add_expense(user_id=user_id, amount=int(amount), category=category, description=description)
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        reply_to_message_id=update.effective_message.id,
        text="Expense added successfully!"
    )


async def delete_expense_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc_id = context.args[0]
    user_id = update.effective_user.id
    
    delete_result = db_client.delete_expense(user_id=user_id,
                            doc_id=ObjectId(doc_id))
    if delete_result:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            reply_to_message_id=update.effective_message.id,
            text="Deleted successfully!"
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            reply_to_message_id=update.effective_message.id,
            text="Problem Occured, Please check bot's log."
        )


async def get_expenses_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    user_id = update.effective_user.id

    if args:
        category = args[0]
        expenses = db_client.get_expenses_by_category(user_id, category)
        text ="Your expenses are:\n"
        for expense in expenses:
            text += (
                f"{expense['amount']} - {expense['category']} - {expense['description']} - {expense['date']} - {expense['document_id']}\n"
    )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            reply_to_message_id=update.effective_message.id,
            text=text
        )
    else:
        total_expenses = db_client.get_expenses(user_id)
        text = "Your expenses are:\n"
        for expense in total_expenses:
            text += (
                f"{expense['amount']} - {expense['category']} - {expense['description']} - {expense['date']} - {expense['document_id']}\n"
            )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_to_message_id=update.effective_message.id,
        )


async def get_categories_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE,):
    user_id = update.effective_user.id
    
    categories = db_client.get_categories(user_id)
    text = f"Your categories are: {', '.join(categories)}"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        reply_to_message_id=update.effective_message.id,
        text=text
    )


async def get_total_expense_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    result = db_client.get_total_expense(user_id)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        reply_to_message_id=update.effective_message.id,
        text=f"Your total expense is: {result}"
    )

async def get_total_expense_by_category_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    
    total_expense = db_client.get_total_expense_by_category(user_id)
    text = "Your total expenses by category are:\n"
    for category, expense in total_expense.items():
        text += f"{category}: {expense}\n"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        reply_to_message_id=update.effective_message.id,
        text=text)

# Error Handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("error:",context.error,"on Update",update)



if __name__ == "__main__":
    # expense_mongo_client = ExpenseMongoClient("mongodb+srv://jigsaw1313:Aramis2427@expenses.0cbt6ew.mongodb.net/", 27017)
    bot = ApplicationBuilder().token(BOT_TOKEN).build()

    # adding handlers
    bot.add_handler(CommandHandler("start", start_command_handler))

    # add all your handlers here
    bot.add_handler(CommandHandler('add', add_expense_command_handler))
    bot.add_handler(CommandHandler('help', help_command_handler))
    bot.add_handler(CommandHandler('get_expenses', get_expenses_command_handler))
    bot.add_handler(CommandHandler('delete', delete_expense_command_handler))
    bot.add_handler(CommandHandler('get_categories', get_categories_command_handler))
    bot.add_handler(CommandHandler('get_total', get_total_expense_command_handler))
    bot.add_handler(CommandHandler('get_total_by_category', get_total_expense_by_category_command_handler))
    bot.add_error_handler(error_handler)
    
    # start bot
    bot.run_polling()

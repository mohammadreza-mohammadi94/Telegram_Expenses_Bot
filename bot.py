import logging
from typing import Final
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from bson.objectid import ObjectId
from mongo_client import ExpenseMongoClient


# Bot Token
BOT_TOKEN : Final = "7079993461:AAGryn5WVrZlREgS8HwRYMpltQEQr7jKXPI"

# Developer Ids whom can access to the bot
dev_ids = [44557320]

# Enable Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


# connect to your mongodb
db_client = ExpenseMongoClient("mongodb+srv://jigsaw1313:Aramis2427@expenses.0cbt6ew.mongodb.net/", 27017)

# Handlers
async def start_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ This method is reposible for running and greeting commands"""
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello Mohammadreza, Let's record your daily expenses",
        reply_to_message_id=update.effective_message.id,
    )

# help message content.
HELP_COMMAND_RESPONSE = """
Greetings! Here are the commands you can use with this bot:

/start -> Begin interacting with the bot.
/add <amount> <category> <description> -> Add new expense.
/delete <document_id> -> Removes expense by document id.
/expenses -> Shows list of all expenses.
/categories -> Shows all categories.
/total -> Show total expenses recorded in database.
/total_by_category -> Shows total expenses for each category.
"""

async def help_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ This function is reposible to show command handlers to user in telegram bot."""
    
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text = HELP_COMMAND_RESPONSE,
        reply_to_message_id=update.effective_message.id
    )


async def add_expense_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ This function is reposible to add new expense to mongodb.
    the usage command inside telegram is -> /add <amount> <category> <description>. The date will be
    updated inside mongodb functions."""
    
    
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
    """ This method is called when the user wants to delete,
    a specific expense. usage command is : /delete <document_id>"""
    
    
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


async def get_total_expense_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ This method is reponsible to show total expense recorded inside database"""
    
    
    user_id = update.effective_user.id
    result = db_client.get_total_expense(user_id)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        reply_to_message_id=update.effective_message.id,
        text=f"Your total expense is: {result}"
    )


async def get_expenses_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ This method is responsible show all expenses and documents recorded in database.
    If user sends a category's name after command , it will be displayed according to that category.
    For example :
        /expenses <category_name>
    Or if user does not specify a category name, the command would be as below:
        /expenses
    it will show all documents, regardless of its category."""
    
    
    args = context.args            # To get catregory name as args.
    user_id = update.effective_user.id

    if args:
        # if user's sends category name.
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
        # if user does not send category name.
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


async def get_categories_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """This method's responsibility is to show categories name."""
    
    
    user_id = update.effective_user.id 
    categories = db_client.get_categories(user_id)
    text = f"Your categories are: {', '.join(categories)}"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        reply_to_message_id=update.effective_message.id,
        text=text
    )


async def get_total_expense_by_category_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ This method will show all expenses by their category."""
    
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


# Creating and running the bot.
if __name__ == "__main__":
    bot = ApplicationBuilder().token(BOT_TOKEN).build()

    # Adding handlers
    bot.add_handler(CommandHandler("start", start_command_handler))
    bot.add_handler(CommandHandler('add', add_expense_command_handler))
    bot.add_handler(CommandHandler('help', help_command_handler))
    bot.add_handler(CommandHandler('expenses', get_expenses_command_handler))
    bot.add_handler(CommandHandler('delete', delete_expense_command_handler))
    bot.add_handler(CommandHandler('categories', get_categories_command_handler))
    bot.add_handler(CommandHandler('total', get_total_expense_command_handler))
    bot.add_handler(CommandHandler('total_by_category', get_total_expense_by_category_command_handler))
    
    # Error handlers
    bot.add_error_handler(error_handler)
    
    # start bot
    bot.run_polling()
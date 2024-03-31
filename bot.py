import logging
from typing import Final
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from bson.objectid import ObjectId
from mongo_client import ExpenseMongoClient
from functools import wraps



# Bot Token
BOT_TOKEN : Final = "7079993461:AAGryn5WVrZlREgS8HwRYMpltQEQr7jKXPI"

# Enable Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# connect to your mongodb
db_client = ExpenseMongoClient("mongodb+srv://jigsaw1313:Aramis2427@expenses.0cbt6ew.mongodb.net/", 27017)

# User Ids whom can access to the bot
LIST_OF_ADMINS = [44557320]

# Decorator to handle access to bot.
def restricted(func):
    ''' This is a decorator that will limit access to the bot
        to only users in LIST_OF_ADMINS variable.
    '''

    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            print(f"Unauthorized access denied for {user_id}.")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Access denied")
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

# Handlers
@restricted
async def start_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ This method is reposible for running and greeting commands."""
    user_name = update.effective_user.name
    
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Hello {user_name}, Let's record your daily expenses",
            reply_to_message_id=update.effective_message.id,
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"An error occurred: {str(e)}",
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
/search_month <month: int> -> Show total expenses per month.
/search_date <start_date> <end_date> -> Show all expenses durint specified date.
"""

@restricted
async def help_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ This function is reposible to show command handlers to user in telegram bot."""
    
    
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = HELP_COMMAND_RESPONSE,
            reply_to_message_id=update.effective_message.id
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"An error occurred: {str(e)}",
            reply_to_message_id=update.effective_message.id,
        )


@restricted
async def add_expense_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ This function is reposible to add new expense to mongodb.
    the usage command inside telegram is -> /add <amount> <category> <description>. The date will be
    updated inside mongodb functions."""
    
    
    try:
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

    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"An error occurred: {str(e)}",
            reply_to_message_id=update.effective_message.id,
        )


@restricted
async def delete_expense_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ This method is called when the user wants to delete,
    a specific expense. usage command is : /delete <document_id>"""
    
    try:
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

    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"An error occurred: {str(e)}",
            reply_to_message_id=update.effective_message.id,
        )


@restricted
async def get_total_expense_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ This method is reponsible to show total expense recorded inside database"""
    
    
    try:    
        user_id = update.effective_user.id
        result = db_client.get_total_expense(user_id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            reply_to_message_id=update.effective_message.id,
            text=f"Your total expense is: {result}"
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"An error occurred: {str(e)}",
            reply_to_message_id=update.effective_message.id,
        )


@restricted
async def get_expenses_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ This method is responsible show all expenses and documents recorded in database.
    If user sends a category's name after command , it will be displayed according to that category.
    For example :
        /expenses <category_name>
    Or if user does not specify a category name, the command would be as below:
        /expenses
    it will show all documents, regardless of its category."""
    
    
    try:
        args = context.args            # To get catregory name 
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
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"An error occurred: {str(e)}",
            reply_to_message_id=update.effective_message.id,
        )


@restricted
async def get_categories_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """This method's responsibility is to show categories name."""
    
    
    try:
        user_id = update.effective_user.id 
        categories = db_client.get_categories(user_id)
        text = f"Your categories are: {', '.join(categories)}"
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            reply_to_message_id=update.effective_message.id,
            text=text
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"An error occurred: {str(e)}",
            reply_to_message_id=update.effective_message.id,
        )


@restricted
async def get_total_expense_by_category_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ 
    This method will show all expenses by their category.
    """
    
    
    try:
        user_id = update.effective_user.id
        total_expense = db_client.get_total_expense_by_category(user_id)
        text = "Your total expenses by category are:\n"
        for category, expense in total_expense.items():
            text += f"{category}: {expense}\n"
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            reply_to_message_id=update.effective_message.id,
            text=text
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"An error occurred: {str(e)}",
            reply_to_message_id=update.effective_message.id,
        )


@restricted
async def search_expense_by_month_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ 
    This method will show all expenses by specified month.
    """
    
    try:
        month = context.args[0]
        expenses_by_month = db_client.get_expenses_by_month(month)
        text =f"Your expenses in month number {month} are:\n"
        
        for expense in expenses_by_month:
            text += (
                f"{expense['amount']} - {expense['category']} - {expense['description']} - {expense['date']} - {expense['_id']}\n"
            )
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            reply_to_message_id=update.effective_message.id,
            text=text
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"An error occurred: {str(e)}",
            reply_to_message_id=update.effective_message.id,
        )


@restricted
async def search_period_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    This function is used to search and retrive all expenses during a given period of date.
    """


    try:
        date1 = context.args[0]
        date2 = context.args[1]

        expenses_date_duration = db_client.search_date(date1, date2)

        text =f"Your expenses during {date1} - {date2} are:\n"
        for expense in expenses_date_duration:
            text += (
                f"{expense['amount']} - {expense['category']} - {expense['description']} - {expense['date']} - {expense['_id']}\n"
            )
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            reply_to_message_id=update.effective_message.id,
            text=text
        )
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"An error occurred: {str(e)}",
            reply_to_message_id=update.effective_message.id,
        )


@restricted
async def unknown_input_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ In case of unknown input message from user this method will return HELP_COMMAND_RESPONSE."""

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        reply_to_message_id=update.effective_message.id,
        text="Sorry, I didn't understand that command.\n" + HELP_COMMAND_RESPONSE
    )

# Error Handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("error:",context.error,"on Update",update)



# Creating and running the bot.
if __name__ == "__main__":
    bot = ApplicationBuilder().token(BOT_TOKEN).build()

    # Adding handlers
    # Command handlers
    bot.add_handler(CommandHandler("start", start_command_handler))
    bot.add_handler(CommandHandler('add', add_expense_command_handler))
    bot.add_handler(CommandHandler('help', help_command_handler))
    bot.add_handler(CommandHandler('expenses', get_expenses_command_handler))
    bot.add_handler(CommandHandler('delete', delete_expense_command_handler))
    bot.add_handler(CommandHandler('categories', get_categories_command_handler))
    bot.add_handler(CommandHandler('total', get_total_expense_command_handler))
    bot.add_handler(CommandHandler('total_by_category', get_total_expense_by_category_command_handler))
    bot.add_handler(CommandHandler('search_month', search_expense_by_month_command_handler))
    bot.add_handler(CommandHandler('search_date', search_period_command_handler))
    # Message handler
    bot.add_handler(MessageHandler(filters.COMMAND, unknown_input_message_handler))
    bot.add_handler(MessageHandler(filters.TEXT, unknown_input_message_handler))
    # Error handlers
    bot.add_error_handler(error_handler)
    
    # start bot
    bot.run_polling()
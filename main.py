import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context.
from data_manager import get_user, update_user

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user_id = update.effective_user.id
    get_user(user_id)  # Ensure user is initialized
    await update.message.reply_text("Hi!")

async def complete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Marks a task as complete and rewards the user."""
    user_id = update.effective_user.id
    user_data = get_user(user_id)

    if not context.args:
        await update.message.reply_text("Please specify a task name. Usage: /complete_task <task_name>")
        return

    task_name = " ".join(context.args)

    # For now, we are not checking if the task exists in user_data['tasks']
    # We just reward the user for reporting completion.
    # Future enhancement: check if task_name is in user_data['tasks']
    # and perhaps remove it or mark it as completed.

    user_data['experience'] += 10
    user_data['gold'] += 5
    update_user(user_id, user_data)

    await update.message.reply_text(f"You completed '{task_name}'! You gained 10 XP and 5 Gold.")

async def failed_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /failed_task command."""
    user_id = update.effective_user.id
    user_data = get_user(user_id)

    if not context.args:
        await update.message.reply_text("Please specify the task/habit you failed. Usage: /failed_task <task_name>")
        return

    task_name = " ".join(context.args)

    user_data['health'] -= 10
    update_user(user_id, user_data)

    await update.message.reply_text(f"You reported failing '{task_name}'. You lost 10 Health.")

    if user_data['health'] <= 0:
        await update.message.reply_text("Your health has reached 0! Be careful!")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays the user's current status."""
    user_id = update.effective_user.id
    user_data = get_user(user_id)

    status_message = (
        f"Your Status:\n"
        f"Health: {user_data['health']}\n"
        f"Experience: {user_data['experience']}\n"
        f"Gold: {user_data['gold']}"
    )
    await update.message.reply_text(text=status_message)

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("YOUR_TELEGRAM_BOT_TOKEN").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("complete_task", complete_task))
    application.add_handler(CommandHandler("failed_task", failed_task))
    application.add_handler(CommandHandler("status", status))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()

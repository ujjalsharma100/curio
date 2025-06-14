import logging
from telegram import Update, User
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import requests


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Telegram bot token
BOT_TOKEN = "7477796128:AAE7BjPgmC2z3jDnfNmDjDENks8jh7Zowvw"

# telegram user ids for subscribers
TELEGRAM_SUBSCRIBER_USER_IDS = [7962940109]

BACKEND_URL = "http://localhost:8453"


def print_user_details(update: Update) -> None:
    """Print detailed information about the user."""
    user = update.effective_user
    chat = update.effective_chat
    
    print("\n=== User Details ===")
    print(f"User ID: {user.id}")
    print(f"Username: @{user.username}")
    print(f"First Name: {user.first_name}")
    print(f"Last Name: {user.last_name}")
    print(f"Language Code: {user.language_code}")
    print(f"Is Bot: {user.is_bot}")
    print(f"Chat Type: {chat.type}")
    print(f"Chat ID: {chat.id}")
    print("===================\n")

def get_curio_application_route_endpoint():
    return "http://localhost:8086/route_telegram_user_message"

def is_user_authorized(user: User) -> bool:
    return user.id in TELEGRAM_SUBSCRIBER_USER_IDS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    print_user_details(update)
    welcome_text = """
    Welcome! I’m Kevin.
It’s no secret—AI is transforming the world at an unprecedented pace. Every day brings breakthroughs, new tools, and evolving ideas. But with so much happening, it’s easy to feel overwhelmed or miss what truly matters to you.

Whether you're a designer, engineer, or in management, staying informed is essential to stay ahead. But not all information is useful to everyone—and that’s where I come in.

I’m here to deliver AI updates and insights tailored to your interests. The more you share with me, the better I can serve you.

So, tell me a bit about yourself—and let’s get started.
    """
    await update.message.reply_text(welcome_text)
    user = update.effective_user
    if user.id not in TELEGRAM_SUBSCRIBER_USER_IDS:
        await update.message.reply_text("Sorry, I am not allowed to help your right now 😔... You have to ask my admin to register you and then I can help you ☺️")



async def route_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    print_user_details(update)
    user = update.effective_user
    
    if is_user_authorized(user):
        curio_application_route_endpint_url = get_curio_application_route_endpoint()
        payload = {
            "telegram_id": user.id, 
            "user_message": update.message.text
        }
        requests.post(curio_application_route_endpint_url, json=payload)
    else:
        await update.message.reply_text("Sorry, I am not allowed to help your right now 😔... You have to ask my admin to register you and then I can help you ☺️")
    

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    # PLEASE REPLACE "YOUR_TELEGRAM_BOT_TOKEN" WITH YOUR ACTUAL BOT TOKEN
    application = Application.builder().token(BOT_TOKEN).build()
    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    # Add the new text message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route_user_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()
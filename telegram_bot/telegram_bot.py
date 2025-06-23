import logging
from telegram import Update, User
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Telegram bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Admin bot token
ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN")

# Admin telegram ID - PLACEHOLDER - replace with actual admin telegram ID
ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "123456789"))

# Constants that don't change
TELEGRAM_API_BASE_URL = "https://api.telegram.org"

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
    base_url = os.getenv("CURIO_BASE_URL", "http://localhost:8086")
    route = os.getenv("CURIO_ROUTE_TELEGRAM_MESSAGE", "/route_telegram_user_message")
    return f"{base_url}{route}"

def is_user_authorized(user: User) -> bool:
    """Check if the user is registered by querying the CurioApplication."""
    curio_base_url = os.getenv("CURIO_BASE_URL", "http://localhost:8086")
    check_url = f"{curio_base_url}/is_user_registered"
    try:
        response = requests.post(check_url, json={"telegram_id": user.id}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("registered", False)
        else:
            return False
    except Exception as e:
        logger.error(f"Error checking user registration: {str(e)}")
        return False

async def send_unregistered_user_notification_to_admin(update: Update) -> None:
    """Send notification to admin bot when an unregistered user tries to use Curio."""
    user = update.effective_user
    chat = update.effective_chat
    
    # Format user details for admin notification
    user_details = f"""
🚨 **Unregistered User Alert**

A user tried to use Curio but isn't registered yet.

**User Details:**
• User ID: `{user.id}`
• Username: @{user.username}
• First Name: {user.first_name}
• Last Name: {user.last_name}
• Language Code: {user.language_code}
• Is Bot: {user.is_bot}
• Chat Type: {chat.type}
• Chat ID: {chat.id}

**Action Required:** Register this user using `/register {user.id}`
"""
    
    # Send message to admin bot
    admin_bot_url = f"{TELEGRAM_API_BASE_URL}/bot{ADMIN_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": ADMIN_TELEGRAM_ID,
        "text": user_details,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(admin_bot_url, json=payload)
        if response.status_code != 200:
            logger.error(f"Failed to send admin notification: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Error sending admin notification: {str(e)}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    print_user_details(update)
    welcome_text = """
    Welcome! I'm Curio.
AI is changing everything—and fast. From breakthrough research to powerful tools, the pace of progress is unlike anything we've seen before. But with so much happening, it's easy to feel lost in the noise. What matters most isn't just staying updated—it's staying relevant.

That's where I come in. I'm not just another information feed. I'm designed to understand you—your interests, your goals, your domain—and bring you the AI insights that matter most to you.

Whether you're a designer, engineer, founder, or in management, you need to stay ahead. AI isn't just about automation—it's about amplifying your productivity, sharpening your edge, and expanding how you think and work.

The more you share, the more precise and valuable I become. I'm here to help you cut through the noise, focus on what's truly useful, and stay one step ahead in a world that doesn't slow down.

Introduce yourself—and let's get started.
    """
    await update.message.reply_text(welcome_text)
    user = update.effective_user
    if not is_user_authorized(user):
        await update.message.reply_text("Sorry, I am not allowed to help your right now 😔... You have to ask my admin to register you and then I can help you ☺️")
        # Send notification to admin
        await send_unregistered_user_notification_to_admin(update)



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
        # Send notification to admin
        await send_unregistered_user_notification_to_admin(update)
    

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
import logging
from telegram import Update, User
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Admin bot token - PLACEHOLDER - replace with actual token
ADMIN_BOT_TOKEN = os.getenv("ADMIN_BOT_TOKEN")

# Admin telegram ID - PLACEHOLDER - replace with actual admin telegram ID
ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "123456789"))


def is_admin_authorized(user: User) -> bool:
    """Check if the user is authorized to use admin commands."""
    return user.id == ADMIN_TELEGRAM_ID


def print_user_details(update: Update) -> None:
    """Print detailed information about the user."""
    user = update.effective_user
    chat = update.effective_chat
    
    print("\n=== Admin User Details ===")
    print(f"User ID: {user.id}")
    print(f"Username: @{user.username}")
    print(f"First Name: {user.first_name}")
    print(f"Last Name: {user.last_name}")
    print(f"Language Code: {user.language_code}")
    print(f"Is Bot: {user.is_bot}")
    print(f"Chat Type: {chat.type}")
    print(f"Chat ID: {chat.id}")
    print(f"Is Admin Authorized: {is_admin_authorized(user)}")
    print("==========================\n")


def get_curio_initialize_user_endpoint():
    base_url = os.getenv("CURIO_BASE_URL", "http://localhost:8086")
    route = os.getenv("CURIO_ROUTE_INITIALIZE_USER", "/add_and_initialize_user")
    return f"{base_url}{route}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    print_user_details(update)
    user = update.effective_user
    
    if not is_admin_authorized(user):
        await update.message.reply_text("❌ Unauthorized access. This bot is restricted to admin use only.")
        return
    
    welcome_text = """
    Welcome to Curio Admin Bot! 🤖

I'm here to help you manage user registrations for the Curio AI assistant.

Available commands:
/register <telegram_id> - Register a new user with the given telegram ID
/deactivate <telegram_id> - Deactivate an existing user
/list_users - List all registered users
/system_message <message> - Send a system message to all users
/send_news_updates_to_all_users - Send the default news update to all users
/reset_limit <telegram_id> - Reset a user's request limit for today to 0
/help - Show this help message

Example: /register 123456789
    """
    await update.message.reply_text(welcome_text)


async def register_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Register a new user with the given telegram ID."""
    print_user_details(update)
    user = update.effective_user
    
    if not is_admin_authorized(user):
        await update.message.reply_text("❌ Unauthorized access. This bot is restricted to admin use only.")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Please provide a telegram ID.\nUsage: /register <telegram_id>")
        return
    
    try:
        telegram_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid telegram ID. Please provide a valid number.")
        return
    
    try:
        # Call curio application to initialize new user
        curio_endpoint = get_curio_initialize_user_endpoint()
        payload = {
            "telegram_id": telegram_id,
            "admin_telegram_id": user.id
        }
        response = requests.post(curio_endpoint, json=payload)
        if response.status_code == 200:
            await update.message.reply_text(f"✅ Successfully registered user with telegram ID {telegram_id}!")
        else:
            await update.message.reply_text(f"⚠️ Failed to register user in Curio application. Status: {response.status_code}\n{response.text}")
    except Exception as e:
        logger.error(f"Error registering user {telegram_id}: {str(e)}")
        await update.message.reply_text(f"❌ Error registering user: {str(e)}")


async def deactivate_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Deactivate a user with the given telegram ID."""
    print_user_details(update)
    user = update.effective_user
    
    if not is_admin_authorized(user):
        await update.message.reply_text("❌ Unauthorized access. This bot is restricted to admin use only.")
        return
    
    if not context.args:
        await update.message.reply_text("❌ Please provide a telegram ID.\nUsage: /deactivate <telegram_id>")
        return
    
    try:
        telegram_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid telegram ID. Please provide a valid number.")
        return
    
    try:
        curio_base_url = os.getenv("CURIO_BASE_URL", "http://localhost:8086")
        deactivate_url = f"{curio_base_url}/deactivate_user"
        payload = {
            "telegram_id": telegram_id,
            "admin_telegram_id": user.id
        }
        response = requests.post(deactivate_url, json=payload)
        
        if response.status_code == 200:
            await update.message.reply_text(f"✅ Successfully deactivated user with telegram ID {telegram_id}.")
        else:
            await update.message.reply_text(f"⚠️ Failed to deactivate user. Status: {response.status_code}\n{response.text}")
    except Exception as e:
        logger.error(f"Error deactivating user {telegram_id}: {str(e)}")
        await update.message.reply_text(f"❌ Error deactivating user: {str(e)}")


async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all registered users."""
    print_user_details(update)
    user = update.effective_user
    
    if not is_admin_authorized(user):
        await update.message.reply_text("❌ Unauthorized access. This bot is restricted to admin use only.")
        return
    
    try:
        curio_base_url = os.getenv("CURIO_BASE_URL", "http://localhost:8086")
        list_url = f"{curio_base_url}/list_users"
        response = requests.get(list_url, timeout=5)
        if response.status_code == 200:
            users = response.json().get("users", [])
            if users:
                user_list = "\n".join([
                    f"• telegram_id: {u['telegram_id']}, user_id: {u['user_id']}, agent_id: {u['agent_id']}" for u in users
                ])
                await update.message.reply_text(f"📋 Registered Users ({len(users)} total):\n{user_list}")
            else:
                await update.message.reply_text("📋 No users registered yet.")
        else:
            await update.message.reply_text(f"❌ Failed to fetch users. Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        await update.message.reply_text(f"❌ Error listing users: {str(e)}")


async def system_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a system message to all users."""
    print_user_details(update)
    user = update.effective_user
    if not is_admin_authorized(user):
        await update.message.reply_text("❌ Unauthorized access. This bot is restricted to admin use only.")
        return
    if not context.args:
        await update.message.reply_text("❌ Please provide a message.\nUsage: /system_message <message>")
        return
    system_message_text = " ".join(context.args)
    try:
        curio_base_url = os.getenv("CURIO_BASE_URL", "http://localhost:8086")
        endpoint = f"{curio_base_url}/send_system_message_to_all_users"
        payload = {
            "admin_telegram_id": user.id,
            "system_message": system_message_text
        }
        response = requests.post(endpoint, json=payload)
        if response.status_code == 200:
            await update.message.reply_text("✅ System message sent to all users.")
        else:
            await update.message.reply_text(f"⚠️ Failed to send system message. Status: {response.status_code}\n{response.text}")
    except Exception as e:
        logger.error(f"Error sending system message: {str(e)}")
        await update.message.reply_text(f"❌ Error sending system message: {str(e)}")


async def send_news_updates_to_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the default system news update to all users."""
    print_user_details(update)
    user = update.effective_user
    if not is_admin_authorized(user):
        await update.message.reply_text("❌ Unauthorized access. This bot is restricted to admin use only.")
        return
    try:
        curio_base_url = os.getenv("CURIO_BASE_URL", "http://localhost:8086")
        endpoint = f"{curio_base_url}/send_system_message_to_all_users"
        payload = {
            "admin_telegram_id": user.id
            # No 'system_message' key, so the backend uses the default
        }
        response = requests.post(endpoint, json=payload)
        if response.status_code == 200:
            await update.message.reply_text("✅ News update sent to all users.")
        else:
            await update.message.reply_text(f"⚠️ Failed to send news update. Status: {response.status_code}\n{response.text}")
    except Exception as e:
        logger.error(f"Error sending news update: {str(e)}")
        await update.message.reply_text(f"❌ Error sending news update: {str(e)}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help message."""
    user = update.effective_user
    
    if not is_admin_authorized(user):
        await update.message.reply_text("❌ Unauthorized access. This bot is restricted to admin use only.")
        return
    
    help_text = """
🤖 Curio Admin Bot Help

Available commands:
/start - Welcome message and basic info
/register <telegram_id> - Register a new user
/deactivate <telegram_id> - Deactivate an existing user
/list_users - Show all registered users
/system_message <message> - Send a system message to all users
/send_news_updates_to_all_users - Send the default news update to all users
/reset_limit <telegram_id> - Reset a user's request limit for today to 0
/help - Show this help message

Examples:
/register 123456789
/deactivate 987654321
/list_users
/system_message Hello, this is a system-wide update!
/send_news_updates_to_all_users
/reset_limit 123456789
    """
    await update.message.reply_text(help_text)


async def reset_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reset a user's request limit for today to 0."""
    print_user_details(update)
    user = update.effective_user
    if not is_admin_authorized(user):
        await update.message.reply_text("❌ Unauthorized access. This bot is restricted to admin use only.")
        return
    if not context.args:
        await update.message.reply_text("❌ Please provide a telegram ID.\nUsage: /reset_limit <telegram_id>")
        return
    try:
        telegram_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid telegram ID. Please provide a valid number.")
        return
    try:
        curio_base_url = os.getenv("CURIO_BASE_URL", "http://localhost:8086")
        reset_url = f"{curio_base_url}/reset_user_request_limit"
        payload = {
            "telegram_id": telegram_id,
            "admin_telegram_id": user.id
        }
        response = requests.post(reset_url, json=payload)
        if response.status_code == 200:
            await update.message.reply_text(f"✅ Successfully reset request limit for user {telegram_id}.")
        else:
            await update.message.reply_text(f"⚠️ Failed to reset request limit. Status: {response.status_code}\n{response.text}")
    except Exception as e:
        logger.error(f"Error resetting request limit for user {telegram_id}: {str(e)}")
        await update.message.reply_text(f"❌ Error resetting request limit: {str(e)}")


def main() -> None:
    """Start the admin bot."""
    # Create the Application and pass it your bot's token.
    # PLEASE REPLACE "YOUR_ADMIN_BOT_TOKEN_HERE" WITH YOUR ACTUAL ADMIN BOT TOKEN
    application = Application.builder().token(ADMIN_BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register_user))
    application.add_handler(CommandHandler("deactivate", deactivate_user))
    application.add_handler(CommandHandler("list_users", list_users))
    application.add_handler(CommandHandler("system_message", system_message))
    application.add_handler(CommandHandler("send_news_updates_to_all_users", send_news_updates_to_all_users))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reset_limit", reset_limit))

    # Run the bot until the user presses Ctrl-C
    logger.info("Starting Curio Admin Bot...")
    application.run_polling()


if __name__ == "__main__":
    main() 
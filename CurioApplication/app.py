from flask import Flask, jsonify, request
from flask_cors import CORS
import message_router
from user_db import CurioUserDB
import uuid
import requests
import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Get environment variables with fallback defaults
AGENT_BASE_URL = os.getenv('AGENT_BASE_URL', 'http://localhost:8087')
AGENT_INITIALIZE_ENDPOINT = os.getenv('AGENT_INITIALIZE_ENDPOINT', '/curio_chat/initialize_agent')
ADMIN_TELEGRAM_ID = os.getenv('ADMIN_TELEGRAM_ID')

@app.route('/route_telegram_user_message', methods=['POST'])
def route_telegram_user_message():
    """
    Handle incoming messages from Telegram users.
    
    This endpoint receives POST requests containing user messages from Telegram.
    It extracts the user message and Telegram ID from the request JSON and forwards
    them to the message router for processing.
    
    Expected JSON payload:
        {
            "user_message": str,  # The message content from the user
            "telegram_id": str    # The Telegram user's unique identifier
        }
    
    Returns:
        None. Any errors during processing are printed to the console.
        
    Raises:
        Exception: Any exceptions during processing are caught and printed.
    """
    try:
        data = request.json
        print(data)
        user_message = data['user_message']
        telegram_id = data['telegram_id']
        
        db = CurioUserDB()

        # Check if user is active
        if not db.is_user_active(int(telegram_id)):
            inactive_message = "Your account has been deactivated. Please contact the administrator."
            try:
                agent_id = db.get_agent_id_from_telegram_id(int(telegram_id))
                message_router.route_agent_message_to_telegram(inactive_message, int(telegram_id), agent_id)
            except ValueError as e:
                print(f"Error sending deactivation message: {e}")
            return jsonify({"message": "User deactivated"}), 403

        # Check daily request limit
        limit_exceeded, current_count = db.check_and_increment_request_count(int(telegram_id))
        
        if limit_exceeded:
            # Send limit exceeded message to user
            limit_message = f"Daily request limit exceeded. You have used {current_count} requests today. Please try again tomorrow."
            message_router.route_agent_message_to_telegram(limit_message, int(telegram_id), db.get_agent_id_from_telegram_id(int(telegram_id)))
            return jsonify({"message": "Daily limit exceeded", "limit_exceeded": True}), 429
        
        # Process the message normally
        message_router.route_telegram_user_message(user_message, telegram_id)
        return jsonify({"message": "telegram message routed", "limit_exceeded": False}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "Error happened!"}), 200

@app.route('/route_agent_message', methods=['POST'])
def route_agent_message():
    """
    Handle incoming messages from agents.
    
    This endpoint receives POST requests containing messages from agents.
    It extracts the agent message and agent ID from the request JSON and forwards
    them to the message router for processing.
    
    Expected JSON payload:
        {
            "agent_message": str,  # The message content from the agent
            "agent_id": str        # The agent's unique identifier
        }
    
    Returns:
        None. Any errors during processing are printed to the console.
        
    Raises:
        Exception: Any exceptions during processing are caught and printed.
    """
    try:
        data = request.json
        print(data)
        agent_message = data['agent_message']
        agent_id = data['agent_id']
        message_router.route_agent_message(agent_message, agent_id)
        return jsonify({"message": "agent message routed"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "Error happened"}), 200

@app.route('/add_and_initialize_user', methods=['POST'])
def add_and_initialize_user():
    """
    Add a new user to the user_db and initialize the agent with the generated agent_id.
    Expects JSON: {"telegram_id": ..., "admin_telegram_id": ...}
    """
    try:
        data = request.json
        print(data)
        telegram_id = data['telegram_id']
        admin_telegram_id = data['admin_telegram_id']
        print(ADMIN_TELEGRAM_ID)
        # Validate admin_telegram_id
        if not ADMIN_TELEGRAM_ID:
            return jsonify({"message": "ADMIN_TELEGRAM_ID not configured", "error": "Server configuration error"}), 500
        
        # Convert both to int for safe comparison
        try:
            admin_telegram_id_int = int(admin_telegram_id)
            configured_admin_id_int = int(ADMIN_TELEGRAM_ID)
        except (ValueError, TypeError):
            return jsonify({"message": "Invalid admin_telegram_id format", "error": "admin_telegram_id must be a valid integer"}), 400
        
        if admin_telegram_id_int != configured_admin_id_int:
            return jsonify({"message": "Unauthorized access", "error": "Invalid admin_telegram_id"}), 403
        
        # Generate unique IDs
        user_id = str(uuid.uuid4())
        agent_id = str(uuid.uuid4())
        print(agent_id)
        db = CurioUserDB()
        # Call agent initialize endpoint
        agent_initialize_url = f"{AGENT_BASE_URL}{AGENT_INITIALIZE_ENDPOINT}"
        payload = {"agent_id": agent_id}
        response = requests.post(agent_initialize_url, json=payload)
        if response.status_code == 200:
            db.add_user(user_id, telegram_id, agent_id)
            return jsonify({"message": "User added and agent initialized", "user_id": user_id, "agent_id": agent_id}), 200
        else:
            return jsonify({"message": "User not added because agent initialization failed", "user_id": user_id, "agent_id": agent_id, "agent_error": response.text}), 500
    except Exception as e:
        print(e)
        return jsonify({"message": "Error happened", "error": str(e)}), 500

@app.route('/is_user_registered', methods=['POST'])
def is_user_registered():
    """
    Check if a user is registered by telegram_id.
    Expects JSON: {"telegram_id": ...}
    Returns: {"registered": true/false}
    """
    try:
        data = request.json
        telegram_id = data['telegram_id']
        db = CurioUserDB()
        registered = db.user_exists(int(telegram_id))
        return jsonify({"registered": registered}), 200
    except Exception as e:
        print(e)
        return jsonify({"registered": False, "error": str(e)}), 500

@app.route('/list_users', methods=['GET'])
def list_users():
    """
    Return a list of all registered users.
    Returns: {"users": [ ... ]}
    """
    try:
        db = CurioUserDB()
        users = db.get_all_users()
        return jsonify({"users": users}), 200
    except Exception as e:
        print(e)
        return jsonify({"users": [], "error": str(e)}), 500

@app.route('/check_user_request_limit', methods=['POST'])
def check_user_request_limit():
    """
    Check a user's current daily request count and limit status.
    Expects JSON: {"telegram_id": ...}
    Returns: {"current_count": int, "daily_limit": int, "limit_exceeded": bool}
    """
    try:
        data = request.json
        telegram_id = data['telegram_id']
        db = CurioUserDB()
        current_count = db.get_user_request_count(int(telegram_id))
        daily_limit = db.DAILY_REQUEST_LIMIT
        limit_exceeded = current_count >= daily_limit
        
        return jsonify({
            "current_count": current_count,
            "daily_limit": daily_limit,
            "limit_exceeded": limit_exceeded
        }), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/deactivate_user', methods=['POST'])
def deactivate_user():
    """
    Deactivate a user.
    Expects JSON: {"telegram_id": ..., "admin_telegram_id": ...}
    """
    try:
        data = request.json
        telegram_id_to_deactivate = data['telegram_id']
        admin_telegram_id = data['admin_telegram_id']

        # Validate admin_telegram_id
        if not ADMIN_TELEGRAM_ID:
            return jsonify({"message": "ADMIN_TELEGRAM_ID not configured", "error": "Server configuration error"}), 500
        
        try:
            admin_telegram_id_int = int(admin_telegram_id)
            configured_admin_id_int = int(ADMIN_TELEGRAM_ID)
        except (ValueError, TypeError):
            return jsonify({"message": "Invalid admin_telegram_id format", "error": "admin_telegram_id must be a valid integer"}), 400
        
        if admin_telegram_id_int != configured_admin_id_int:
            return jsonify({"message": "Unauthorized access", "error": "Invalid admin_telegram_id"}), 403

        db = CurioUserDB()
        db.deactivate_user(int(telegram_id_to_deactivate))
        
        return jsonify({"message": f"User {telegram_id_to_deactivate} deactivated"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "Error happened", "error": str(e)}), 500

@app.route('/send_system_message_to_all_users', methods=['POST'])
def send_system_message_to_all_users():
    """
    Admin endpoint to send a system message to all active users.
    Expects JSON: {"admin_telegram_id": ..., "system_message": ...}
    """
    try:
        data = request.json
        admin_telegram_id = data.get('admin_telegram_id')
        system_message = data.get('system_message', '[System] I think its time to get some new updates')

        # Validate admin_telegram_id
        if not ADMIN_TELEGRAM_ID:
            return jsonify({"message": "ADMIN_TELEGRAM_ID not configured", "error": "Server configuration error"}), 500
        try:
            admin_telegram_id_int = int(admin_telegram_id)
            configured_admin_id_int = int(ADMIN_TELEGRAM_ID)
        except (ValueError, TypeError):
            return jsonify({"message": "Invalid admin_telegram_id format", "error": "admin_telegram_id must be a valid integer"}), 400
        if admin_telegram_id_int != configured_admin_id_int:
            return jsonify({"message": "Unauthorized access", "error": "Invalid admin_telegram_id"}), 403

        # Send the system message
        message_router.send_system_news_update_to_all_users(system_message)
        return jsonify({"message": "System message sent to all users."}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "Error happened", "error": str(e)}), 500

if __name__ == '__main__':
    # Set up scheduler for system news update
    scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Kolkata'))
    scheduler.add_job(
        message_router.send_system_news_update_to_all_users,
        CronTrigger(hour=9, minute=0),
        id='morning_news_update',
        replace_existing=True
    )
    scheduler.add_job(
        message_router.send_system_news_update_to_all_users,
        CronTrigger(hour=17, minute=0),
        id='evening_news_update',
        replace_existing=True
    )
    scheduler.start()

    app.run(host="0.0.0.0", port=8086, debug=True)

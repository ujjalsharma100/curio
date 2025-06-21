from flask import Flask, jsonify, request
from flask_cors import CORS
import message_router
from user_db import CurioUserDB
import uuid
import requests
import os
from dotenv import load_dotenv

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
        message_router.route_telegram_user_message(user_message, telegram_id)
        return jsonify({"message": "telegram message routed"}), 200
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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8086, debug=True)

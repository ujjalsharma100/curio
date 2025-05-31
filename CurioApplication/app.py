from flask import Flask, jsonify, request
from flask_cors import CORS
import message_router

# Initialize Flask app
app = Flask(__name__)
CORS(app)

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
        return jsonify({"message": "Error happened!"}), 400

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
        return jsonify({"message": "Error happened"}), 400


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8086, debug=True)

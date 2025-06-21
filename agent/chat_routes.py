from flask import Blueprint, request, jsonify
import requests
from ai_person.ai_person import AiPerson

# Create blueprint
chat_bp = Blueprint('curio_chat', __name__, url_prefix='/curio_chat')

aiPerson = AiPerson()

@chat_bp.route('/send_user_message', methods=['POST'])
def send_user_message():
    """
    Handle incoming user messages from the chat interface.
    
    This route receives POST requests containing user messages, processes them,
    and triggers the agent's response mechanism.
    
    Returns:
        None: Currently just prints the message (TODO: implement agent processing)
    """
    try:
        data = request.json
        user_message = data["user_message"]
        agent_id = data["agent_id"]
        print(user_message)

        # TODO: Pass the user message into the agent and process 
        aiPerson.hear_text(agent_id, user_message)

        return jsonify({"message": "user message sent to agent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/initialize_agent', methods=['POST'])
def initialize_agent():
    """
    Initialize a new agent_id in the system (personality, user info, short term memory, etc).
    Expects JSON: {"agent_id": "..."}
    """
    try:
        data = request.json
        agent_id = data["agent_id"]
        aiPerson.initialize_agent(agent_id)
        return jsonify({"message": f"Agent {agent_id} initialized."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

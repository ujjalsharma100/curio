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
    data = request.json
    user_message = data["user_message"]
    print(user_message)

    # TODO: Pass the user message into the agent and process 
    aiPerson.hear_text(user_message)

    return jsonify({"message": "user message sent to agent"}), 200

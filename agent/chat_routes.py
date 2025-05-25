from flask import Blueprint, request
import requests

# Create blueprint
chat_bp = Blueprint('curio_chat', __name__, url_prefix='/curio_chat')

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


def send_agent_message(agent_message):
    """
    Send a message from the agent back to the main application.
    
    Args:
        agent_message (str): The message content to be sent from the agent
        
    This function sends a POST request to the main Curio application with
    the agent's message and ID. The message is routed to the appropriate
    endpoint for display to the user.
    """
    agent_id = get_agent_id()
    curio_app_url = get_curio_app_url()
    payload = {
        "agent_id": agent_id,
        "agent_message": agent_message
    }
    requests.post(curio_app_url, payload)


def get_agent_id():
    """
    Get the unique identifier for this agent instance.
    
    Returns:
        int: The agent's unique identifier (currently hardcoded to 123)
    """
    return 123


def get_curio_app_url():
    """
    Get the URL endpoint for the main Curio application.
    
    Returns:
        str: The URL where agent messages should be sent
              (currently set to localhost:8086)
    """
    return "http://localhost:8086/route_agent_message"
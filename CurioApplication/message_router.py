import requests
from typing import Dict, Any

def route_telegram_user_message(user_message: str, telegram_id: int) -> None:
    """Route a message from a Telegram user to their corresponding agent endpoint.
    
    Args:
        user_message (str): The message text received from the Telegram user
        telegram_id (int): The Telegram user's unique identifier
        
    Returns:
        None: The function makes a POST request to the agent endpoint but doesn't return anything
    """
    agent_endpoint_url = get_agent_endpoint_from_telegram_id(telegram_id)

    payload = {
        "user_message": user_message
    }

    requests.post(agent_endpoint_url, json=payload)


def route_agent_message(agent_message: str, agent_id: str) -> None:
    """Route a message from an agent to the corresponding Telegram user.
    
    Args:
        agent_message (str): The message text from the agent to be sent to the user
        agent_id (str): The unique identifier of the agent
        
    Returns:
        None: The function routes the message but doesn't return anything
    """
    route_agent_message_to_telegram(agent_message, agent_id)


def get_agent_endpoint_from_telegram_id(telegram_id: int) -> str:
    """Get the endpoint URL for the agent associated with a Telegram user.
    
    Args:
        telegram_id (int): The Telegram user's unique identifier
        
    Returns:
        str: The URL endpoint where agent messages should be sent
    """
    return "http://localhost:8087/curio_chat/send_user_message"


def route_agent_message_to_telegram(agent_message: str, agent_id: str) -> None:
    """Send a message from an agent to a Telegram user.
    
    Args:
        agent_message (str): The message text to be sent to the Telegram user
        agent_id (str): The unique identifier of the agent
        
    Returns:
        None: The function makes a POST request to Telegram API but doesn't return anything
    """
    telegram_id = get_user_telegram_id_from_agent_id(agent_id)
    telegram_url = get_telegram_endpoint_from_agent_id(agent_id)
    
    payload: Dict[str, Any] = {
        "chat_id": telegram_id,
        "text": agent_message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }

    requests.post(telegram_url, json=payload)


def get_user_telegram_id_from_agent_id(agent_id: str) -> int:
    """Get the Telegram user ID associated with an agent ID.
    
    Args:
        agent_id (str): The unique identifier of the agent
        
    Returns:
        int: The Telegram user's unique identifier
    """
    print(agent_id)
    return 7962940109


def get_telegram_endpoint_from_agent_id(agent_id: str) -> str:
    """Get the Telegram API endpoint URL for sending messages.
    
    Args:
        agent_id (str): The unique identifier of the agent
        
    Returns:
        str: The Telegram API endpoint URL for sending messages
    """
    print(agent_id)
    TELEGRAM_API_URL = "https://api.telegram.org/bot7477796128:AAE7BjPgmC2z3jDnfNmDjDENks8jh7Zowvw/sendMessage"
    return TELEGRAM_API_URL
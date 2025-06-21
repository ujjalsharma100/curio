import requests
from typing import Dict, Any
from user_db import CurioUserDB

def route_telegram_user_message(user_message: str, telegram_id: int) -> None:
    """Route a message from a Telegram user to their corresponding agent endpoint using the DB."""
    db = CurioUserDB()
    agent_id = db.get_agent_id_from_telegram_id(telegram_id)
    agent_endpoint_url = db.get_agent_endpoint_from_agent_id(agent_id)
    payload = {
        "user_message": user_message,
        "agent_id": agent_id
    }
    requests.post(agent_endpoint_url, json=payload)


def route_agent_message(agent_message: str, agent_id: str) -> None:
    """Route a message from an agent to the corresponding Telegram user using the DB."""
    db = CurioUserDB()
    telegram_id = db.get_telegram_id_from_agent_id(agent_id)
    route_agent_message_to_telegram(agent_message, telegram_id, agent_id)


def route_agent_message_to_telegram(agent_message: str, telegram_id: int, agent_id: str) -> None:
    """Send a message from an agent to a Telegram user using the DB."""
    db = CurioUserDB()
    telegram_url = db.get_telegram_endpoint_from_agent_id(agent_id)
    payload: Dict[str, Any] = {
        "chat_id": telegram_id,
        "text": agent_message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    requests.post(telegram_url, json=payload)
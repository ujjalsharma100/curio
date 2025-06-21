import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class CurioUserDB:
    DB_PATH = os.path.join(os.path.dirname(__file__), 'curio_users.db')
    
    # Get environment variables with fallback defaults
    DEFAULT_AGENT_BASE_URL = os.getenv('AGENT_BASE_URL', 'http://localhost:8087')
    DEFAULT_AGENT_ENDPOINT = os.getenv('AGENT_ENDPOINT', '/curio_chat/send_user_message')
    DEFAULT_TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7477796128:AAE7BjPgmC2z3jDnfNmDjDENks8jh7Zowvw')
    
    # Constants that don't change
    TELEGRAM_API_BASE_URL = "https://api.telegram.org"

    def __init__(self):
        self._ensure_db()

    def _ensure_db(self):
        if not os.path.exists(self.DB_PATH):
            self._create_db()

    def _create_db(self):
        conn = sqlite3.connect(self.DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT UNIQUE,
                telegram_id INTEGER UNIQUE,
                agent_id TEXT UNIQUE
            )
        ''')
        conn.commit()
        conn.close()

    def get_agent_id_from_telegram_id(self, telegram_id: int) -> str:
        conn = sqlite3.connect(self.DB_PATH)
        c = conn.cursor()
        c.execute('SELECT agent_id FROM users WHERE telegram_id = ?', (telegram_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return row[0]
        raise ValueError(f"No agent_id found for telegram_id {telegram_id}")

    def get_telegram_id_from_agent_id(self, agent_id: str) -> int:
        conn = sqlite3.connect(self.DB_PATH)
        c = conn.cursor()
        c.execute('SELECT telegram_id FROM users WHERE agent_id = ?', (agent_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return row[0]
        raise ValueError(f"No telegram_id found for agent_id {agent_id}")

    def get_agent_endpoint_from_agent_id(self, agent_id: str) -> str:
        # In a real app, you might store endpoint per agent. For now, return default.
        return f"{self.DEFAULT_AGENT_BASE_URL}{self.DEFAULT_AGENT_ENDPOINT}"

    def get_telegram_endpoint_from_agent_id(self, agent_id: str) -> str:
        # In a real app, you might store endpoint per agent. For now, return default.
        return f"{self.TELEGRAM_API_BASE_URL}/bot{self.DEFAULT_TELEGRAM_BOT_TOKEN}/sendMessage"

    def add_user(self, user_id: str, telegram_id: int, agent_id: str):
        conn = sqlite3.connect(self.DB_PATH)
        c = conn.cursor()
        c.execute('INSERT OR IGNORE INTO users (user_id, telegram_id, agent_id) VALUES (?, ?, ?)', (user_id, telegram_id, agent_id))
        conn.commit()
        conn.close() 
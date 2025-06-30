import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime, date

# Load environment variables from .env file
load_dotenv()

class CurioUserDB:
    DB_PATH = os.path.join(os.path.dirname(__file__), 'curio_users.db')
    
    # Get environment variables with fallback defaults
    DEFAULT_AGENT_BASE_URL = os.getenv('AGENT_BASE_URL', 'http://localhost:8087')
    DEFAULT_AGENT_ENDPOINT = os.getenv('AGENT_ENDPOINT', '/curio_chat/send_user_message')
    DEFAULT_TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7477796128:AAE7BjPgmC2z3jDnfNmDjDENks8jh7Zowvw')
    DAILY_REQUEST_LIMIT = int(os.getenv('DAILY_REQUEST_LIMIT', '30'))
    
    # Constants that don't change
    TELEGRAM_API_BASE_URL = "https://api.telegram.org"

    def __init__(self):
        self._ensure_db()

    def _ensure_db(self):
        if not os.path.exists(self.DB_PATH):
            self._create_db()
        else:
            # Ensure the request_tracking table exists even if DB already exists
            self._create_request_tracking_table()

    def _create_db(self):
        conn = sqlite3.connect(self.DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT UNIQUE,
                telegram_id INTEGER UNIQUE,
                agent_id TEXT UNIQUE,
                active BOOLEAN NOT NULL DEFAULT 1
            )
        ''')
        self._create_request_tracking_table(conn)
        conn.commit()
        conn.close()

    def _create_request_tracking_table(self, conn=None):
        """Create the request tracking table if it doesn't exist."""
        if conn is None:
            conn = sqlite3.connect(self.DB_PATH)
        
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS request_tracking (
                telegram_id INTEGER,
                request_date DATE,
                request_count INTEGER DEFAULT 0,
                PRIMARY KEY (telegram_id, request_date)
            )
        ''')
        
        if conn is None:
            conn.commit()
            conn.close()

    def check_and_increment_request_count(self, telegram_id: int) -> tuple[bool, int]:
        """
        Check if user has exceeded daily limit and increment request count.
        
        Returns:
            tuple: (limit_exceeded: bool, current_count: int)
        """
        today = date.today().isoformat()
        
        conn = sqlite3.connect(self.DB_PATH)
        c = conn.cursor()
        
        # Get current count for today
        c.execute('''
            SELECT request_count FROM request_tracking 
            WHERE telegram_id = ? AND request_date = ?
        ''', (telegram_id, today))
        
        row = c.fetchone()
        current_count = row[0] if row else 0
        
        # Check if limit exceeded
        if current_count >= self.DAILY_REQUEST_LIMIT:
            conn.close()
            return True, current_count
        
        # Increment count
        if row:
            c.execute('''
                UPDATE request_tracking 
                SET request_count = request_count + 1 
                WHERE telegram_id = ? AND request_date = ?
            ''', (telegram_id, today))
        else:
            c.execute('''
                INSERT INTO request_tracking (telegram_id, request_date, request_count)
                VALUES (?, ?, 1)
            ''', (telegram_id, today))
        
        conn.commit()
        conn.close()
        
        return False, current_count + 1

    def get_user_request_count(self, telegram_id: int) -> int:
        """Get the current request count for a user today."""
        today = date.today().isoformat()
        
        conn = sqlite3.connect(self.DB_PATH)
        c = conn.cursor()
        c.execute('''
            SELECT request_count FROM request_tracking 
            WHERE telegram_id = ? AND request_date = ?
        ''', (telegram_id, today))
        
        row = c.fetchone()
        conn.close()
        
        return row[0] if row else 0

    def is_user_active(self, telegram_id: int) -> bool:
        conn = sqlite3.connect(self.DB_PATH)
        c = conn.cursor()
        c.execute('SELECT active FROM users WHERE telegram_id = ?', (telegram_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return bool(row[0])
        return False

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

    def user_exists(self, telegram_id: int) -> bool:
        conn = sqlite3.connect(self.DB_PATH)
        c = conn.cursor()
        c.execute('SELECT 1 FROM users WHERE telegram_id = ?', (telegram_id,))
        exists = c.fetchone() is not None
        conn.close()
        return exists

    def deactivate_user(self, telegram_id: int):
        conn = sqlite3.connect(self.DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE users SET active = 0 WHERE telegram_id = ?', (telegram_id,))
        conn.commit()
        conn.close()

    def get_all_users(self):
        conn = sqlite3.connect(self.DB_PATH)
        c = conn.cursor()
        c.execute('SELECT user_id, telegram_id, agent_id, active FROM users')
        users = [
            {"user_id": row[0], "telegram_id": row[1], "agent_id": row[2], "active": bool(row[3])}
            for row in c.fetchall()
        ]
        conn.close()
        return users 
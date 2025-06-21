import sqlite3
import os

class TelegramUserDB:
    DB_PATH = os.path.join(os.path.dirname(__file__), 'telegram_users.db')

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
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE
            )
        ''')
        conn.commit()
        conn.close()

    def add_user(self, telegram_id: int):
        conn = sqlite3.connect(self.DB_PATH)
        c = conn.cursor()
        c.execute('INSERT OR IGNORE INTO users (telegram_id) VALUES (?)', (telegram_id,))
        conn.commit()
        conn.close()

    def user_exists(self, telegram_id: int) -> bool:
        conn = sqlite3.connect(self.DB_PATH)
        c = conn.cursor()
        c.execute('SELECT 1 FROM users WHERE telegram_id = ?', (telegram_id,))
        exists = c.fetchone() is not None
        conn.close()
        return exists

    def get_all_users(self):
        conn = sqlite3.connect(self.DB_PATH)
        c = conn.cursor()
        c.execute('SELECT telegram_id FROM users')
        users = [row[0] for row in c.fetchall()]
        conn.close()
        return users 
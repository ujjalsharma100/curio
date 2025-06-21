import sqlite3
import json
import os
from typing import List, Optional

class ShortTermMemoryDB:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(current_dir, "short_term_memory.db")
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_buffers (
                    agent_id TEXT PRIMARY KEY,
                    buffer_json TEXT
                )
                """
            )
            conn.commit()

    def get_buffer(self, agent_id: str) -> List[str]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT buffer_json FROM conversation_buffers WHERE agent_id = ?",
                (agent_id,)
            )
            row = cursor.fetchone()
            if row and row[0]:
                try:
                    return json.loads(row[0])
                except json.JSONDecodeError:
                    return []
            return []

    def set_buffer(self, agent_id: str, buffer: List[str]):
        buffer_json = json.dumps(buffer)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "REPLACE INTO conversation_buffers (agent_id, buffer_json) VALUES (?, ?)",
                (agent_id, buffer_json)
            )
            conn.commit() 
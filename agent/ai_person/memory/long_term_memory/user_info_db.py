import sqlite3
import os
import json
from typing import Dict, Optional
from datetime import datetime
import logging

# Setup logging for user info database
def setup_user_info_db_logging():
    """Setup logging for the user info database module."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, f"user_info_db_{datetime.now().strftime('%Y%m%d')}.log")
    logger = logging.getLogger("ai_person.memory.user_info_db")
    logger.setLevel(logging.DEBUG)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

logger = setup_user_info_db_logging()

class UserInfoDB:
    def __init__(self, db_path: str = "user_info.db"):
        """Initialize the user info SQLite database."""
        logger.info("Initializing UserInfoDB")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(current_dir, db_path)
        logger.debug(f"SQLite database path: {self.db_path}")
        self._create_tables()
        logger.info("UserInfoDB initialization complete")

    def _create_tables(self):
        """Create the user_info table if it doesn't exist."""
        logger.debug("Creating user_info table if it doesn't exist")
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_info (
                        agent_id TEXT PRIMARY KEY,
                        user_info TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                logger.debug("user_info table created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating user_info table: {str(e)}", exc_info=True)
            raise

    def get_user_info(self, agent_id: str) -> Optional[Dict]:
        """Retrieve user info for a given agent_id as a dict."""
        logger.debug(f"Retrieving user info for agent_id: {agent_id}")
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_info FROM user_info WHERE agent_id = ?
                ''', (agent_id,))
                row = cursor.fetchone()
                if row and row[0]:
                    try:
                        user_info = json.loads(row[0])
                        logger.debug(f"User info found for agent_id: {agent_id}")
                        return user_info
                    except Exception as e:
                        logger.error(f"Error decoding user_info JSON: {str(e)}", exc_info=True)
                        return None
                else:
                    logger.info(f"No user info found for agent_id: {agent_id}")
                    return None
        except Exception as e:
            logger.error(f"Error retrieving user info: {str(e)}", exc_info=True)
            return None

    def set_user_info(self, agent_id: str, user_info: Dict) -> bool:
        """Set or update user info for a given agent_id as a JSON string."""
        logger.info(f"Setting user info for agent_id: {agent_id}")
        try:
            user_info_json = json.dumps(user_info)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO user_info (agent_id, user_info, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(agent_id) DO UPDATE SET
                        user_info=excluded.user_info,
                        updated_at=CURRENT_TIMESTAMP
                ''', (agent_id, user_info_json))
                conn.commit()
                logger.info(f"User info set/updated for agent_id: {agent_id}")
                return True
        except Exception as e:
            logger.error(f"Error setting user info: {str(e)}", exc_info=True)
            return False 
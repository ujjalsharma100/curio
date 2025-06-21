import json
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Personality:
    """Manages the AI personality data and behavior, segmented by agent_id and stored in SQLite."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the Personality class with a SQLite DB path."""
        if db_path is None:
            db_path = str(Path(os.path.dirname(__file__)) / "personality.db")
        self._db_path = db_path
        self._ensure_db()

    def _ensure_db(self) -> None:
        """Ensure the SQLite database and table exist."""
        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS personalities (
                        agent_id TEXT PRIMARY KEY,
                        personality_data TEXT NOT NULL
                    )
                ''')
                conn.commit()
        except Exception as e:
            logger.error(f"Error ensuring database: {e}", exc_info=True)
            raise

    def _load_personality_data(self, agent_id: str) -> Dict[str, Any]:
        """Load personality data for a given agent_id from the database."""
        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT personality_data FROM personalities WHERE agent_id = ?", (agent_id,))
                row = cursor.fetchone()
                if row is None:
                    logger.warning(f"No personality found for agent_id '{agent_id}', creating empty data")
                    data = {"conversational_behavior": ""}
                    self._save_personality_data(agent_id, data)
                    return data
                loaded_data = json.loads(row[0])
                if not isinstance(loaded_data, dict):
                    raise ValueError("Loaded personality data is not a dictionary")
                logger.info(f"Successfully loaded personality data for agent_id '{agent_id}'")
                return loaded_data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in personality data for agent_id '{agent_id}': {e}")
            return {"conversational_behavior": ""}
        except Exception as e:
            logger.error(f"Error loading personality data for agent_id '{agent_id}': {e}", exc_info=True)
            return {"conversational_behavior": ""}

    def _save_personality_data(self, agent_id: str, personality_data: Dict[str, Any]) -> None:
        """Save personality data for a given agent_id to the database."""
        if not isinstance(personality_data, dict):
            raise ValueError("Personality data must be a dictionary")
        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.cursor()
                json_data = json.dumps(personality_data, ensure_ascii=False)
                cursor.execute('''
                    INSERT INTO personalities (agent_id, personality_data)
                    VALUES (?, ?)
                    ON CONFLICT(agent_id) DO UPDATE SET personality_data=excluded.personality_data
                ''', (agent_id, json_data))
                conn.commit()
            logger.info(f"Successfully saved personality data for agent_id '{agent_id}'")
        except Exception as e:
            logger.error(f"Error saving personality data for agent_id '{agent_id}': {e}", exc_info=True)
            raise

    def get_personality_data(self, agent_id: str) -> Dict[str, Any]:
        """Get the complete personality data for a given agent_id."""
        return self._load_personality_data(agent_id).copy()  # Return a copy to prevent external modification

    def get_conversational_behavior(self, agent_id: str) -> str:
        """Get the current conversational behavior text for a given agent_id."""
        behavior = self._load_personality_data(agent_id).get("conversational_behavior", "")
        if not isinstance(behavior, str):
            logger.warning(f"Conversational behavior for agent_id '{agent_id}' is not a string, converting to string")
            behavior = str(behavior)
        return behavior

    def update_conversational_behavior(self, agent_id: str, new_behavior: str) -> None:
        """Update the conversational behavior text for a given agent_id."""
        if not isinstance(new_behavior, str):
            raise ValueError("New behavior must be a string")
        logger.info(f"Updating conversational behavior for agent_id '{agent_id}'")
        data = self._load_personality_data(agent_id)
        data["conversational_behavior"] = new_behavior
        self._save_personality_data(agent_id, data)

    def get_personality_prompt_text(self, agent_id: str) -> str:
        """Generate the complete personality prompt text for a given agent_id."""
        behavior = self.get_conversational_behavior(agent_id)
        final_text = f"""
        You are a funny person.
        You like to make jokes every now and then.

        Conversational behavior:
        {behavior}
        """
        return final_text

    def initialize_personality(self, agent_id: str) -> None:
        """Initialize a new agent_id with default personality data if not present."""
        if self._load_personality_data(agent_id).get("conversational_behavior", None) == "":
            # Already initialized (or just created as empty)
            return
        default_data = {"conversational_behavior": ""}
        self._save_personality_data(agent_id, default_data)
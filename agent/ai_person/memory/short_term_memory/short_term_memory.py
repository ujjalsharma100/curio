from collections import deque
from typing import Optional
from .short_term_memory_db import ShortTermMemoryDB

class ShortTermMemory:
    def __init__(self, maxlen: int = 20, db_path: Optional[str] = None):
        """
        Initialize the short term memory with agent_id-based segmentation using SQLite.
        Args:
            maxlen: Maximum length of the conversation buffer (default 20).
            db_path: Optional path to the SQLite DB file.
        """
        self.maxlen = maxlen
        self.db = ShortTermMemoryDB(db_path)

    def _load_conversation_buffer(self, agent_id: str) -> deque:
        """Load the conversation buffer for the given agent_id from the DB."""
        buffer = self.db.get_buffer(agent_id)
        return deque(buffer, maxlen=self.maxlen)

    def _save_conversation_buffer(self, agent_id: str, buffer: deque) -> None:
        """Save the conversation buffer for the given agent_id to the DB."""
        self.db.set_buffer(agent_id, list(buffer))

    def add_to_conversation_buffer(self, agent_id: str, dialogue_with_timestamp: str) -> None:
        """
        Add a dialogue to the conversation buffer for the given agent_id and persist it.
        If the buffer is full, the oldest dialogue will be automatically removed.
        Args:
            agent_id: The agent's unique identifier.
            dialogue_with_timestamp: The dialogue to add to the buffer.
        """
        buffer = self._load_conversation_buffer(agent_id)
        buffer.append(dialogue_with_timestamp)
        self._save_conversation_buffer(agent_id, buffer)

    def get_current_conversation(self, agent_id: str) -> str:
        """
        Returns the current conversation for the given agent_id as a single string,
        with each dialogue on a new line.
        Always loads the latest state from the DB to ensure consistency.
        Args:
            agent_id: The agent's unique identifier.
        """
        buffer = self._load_conversation_buffer(agent_id)
        return "\n".join(buffer)

    def initialize_short_term_memory(self, agent_id: str) -> None:
        """Initialize the short term memory buffer for a new agent_id (empty buffer)."""
        if not self.db.get_buffer(agent_id):
            self.db.set_buffer(agent_id, [])
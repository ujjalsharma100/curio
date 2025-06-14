from collections import deque
import json
import os
from typing import Optional

class ShortTermMemory:
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the short term memory with optional persistence.

        Args:
            storage_path: Path to the JSON file where conversations will be stored.
                          If None, defaults to 'conversation_buffer.json' in the same directory as this file.
        """
        if storage_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            storage_path = os.path.join(current_dir, "conversation_buffer.json")
        self.storage_path = storage_path
        self.conversation_buffer = deque(maxlen=20)
        self._load_conversation_buffer()

    def _load_conversation_buffer(self) -> None:
        """Load the conversation buffer from the JSON file if it exists."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    saved_buffer = json.load(f)
                    self.conversation_buffer = deque(saved_buffer, maxlen=20)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading conversation buffer: {e}")

    def _save_conversation_buffer(self) -> None:
        """Save the current conversation buffer to the JSON file."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(list(self.conversation_buffer), f)
                print("saved to converstation json")
        except IOError as e:
            print(f"Error saving conversation buffer: {e}")

    def add_to_conversation_buffer(self, dialogue_with_timestamp: str) -> None:
        """
        Add a dialogue to the conversation buffer and persist it.
        If the buffer is full, the oldest dialogue will be automatically removed.
        
        Args:
            dialogue: The dialogue to add to the buffer
        """
        self._load_conversation_buffer()
        self.conversation_buffer.append(dialogue_with_timestamp)
        self._save_conversation_buffer()
        self._load_conversation_buffer()

    def get_current_conversation(self) -> str:
        """
        Returns the current conversation as a single string,
        with each dialogue on a new line.
        Always loads the latest state from disk to ensure consistency.
        """
        self._load_conversation_buffer()
        return "\n".join(self.conversation_buffer)
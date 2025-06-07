import json
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Personality:
    """Manages the AI personality data and behavior."""
    
    def __init__(self):
        """Initialize the Personality class with a JSON file path and empty data."""
        self._json_path = Path(os.path.dirname(__file__)) / "personality.json"
        self._personality_data: Dict[str, Any] = {}
        self._load_personality_data()

    def _load_personality_data(self) -> None:
        """Load personality data from JSON file with error handling and logging."""
        try:
            if not self._json_path.exists():
                logger.warning(f"Personality file not found at {self._json_path}, creating empty data")
                self._personality_data = {"conversational_behavior": ""}
                self._save_personality_data(self._personality_data)
                return

            with open(self._json_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                if not isinstance(loaded_data, dict):
                    raise ValueError("Loaded personality data is not a dictionary")
                self._personality_data = loaded_data
                logger.info("Successfully loaded personality data")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in personality file: {e}")
            self._personality_data = {"conversational_behavior": ""}
        except Exception as e:
            logger.error(f"Error loading personality data: {e}", exc_info=True)
            self._personality_data = {"conversational_behavior": ""}

    def _save_personality_data(self, personality_data: Dict[str, Any]) -> None:
        """Save personality data to JSON file with validation and error handling.
        
        Args:
            personality_data: Dictionary containing personality data to save
            
        Raises:
            ValueError: If personality_data is not a dictionary
        """
        if not isinstance(personality_data, dict):
            raise ValueError("Personality data must be a dictionary")
            
        try:
            # Ensure the directory exists
            self._json_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self._json_path, 'w', encoding='utf-8') as f:
                json.dump(personality_data, f, indent=4, ensure_ascii=False)
            logger.info("Successfully saved personality data")
        except Exception as e:
            logger.error(f"Error saving personality data: {e}", exc_info=True)
            raise

    def get_personality_data(self) -> Dict[str, Any]:
        """Get the complete personality data.
        
        Returns:
            Dict[str, Any]: The complete personality data dictionary
        """
        self._load_personality_data()
        return self._personality_data.copy()  # Return a copy to prevent external modification

    def get_conversational_behavior(self) -> str:
        """Get the current conversational behavior text.
        
        Returns:
            str: The current conversational behavior text
        """
        self._load_personality_data()
        behavior = self._personality_data.get("conversational_behavior", "")
        if not isinstance(behavior, str):
            logger.warning("Conversational behavior is not a string, converting to string")
            behavior = str(behavior)
        return behavior

    def update_conversational_behavior(self, new_behavior: str) -> None:
        """Update the conversational behavior text.
        
        Args:
            new_behavior: String containing the new conversational behavior text
            
        Raises:
            ValueError: If new_behavior is not a string
        """
        if not isinstance(new_behavior, str):
            raise ValueError("New behavior must be a string")
            
        logger.info("Updating conversational behavior")
        self._load_personality_data()
        self._personality_data["conversational_behavior"] = new_behavior
        self._save_personality_data(self._personality_data)

    def get_personality_prompt_text(self) -> str:
        """Generate the complete personality prompt text.
        
        Returns:
            str: The formatted personality prompt text
        """
        behavior = self.get_conversational_behavior()
        final_text = f"""
        You are a funny person.
        You like to make jokes every now and then.

        Conversational behavior:
        {behavior}
        """
        return final_text
from typing import Dict, Optional
from .user_info_db import UserInfoDB
import os
import json

class UserInfo:
    def __init__(self):
        self.db = UserInfoDB()
        # Load the default template from user_info.json
        template_path = os.path.join(os.path.dirname(__file__), "user_info.json")
        try:
            with open(template_path, 'r') as f:
                self.default_template = json.load(f)
        except Exception:
            self.default_template = {}

    def get_user_info(self, agent_id: str) -> Dict:
        """Get all user information for a given agent_id as a dictionary"""
        user_info = self.db.get_user_info(agent_id)
        if user_info is None:
            # Return a copy of the default template
            return dict(self.default_template)
        return user_info

    def update_user_info(self, agent_id: str, field: str, value) -> bool:
        """Update a specific field of user information for a given agent_id
        Args:
            agent_id: The agent identifier
            field: The field to update (arbitrary key in user_info dict)
            value: The new value for the field
        Returns:
            bool: True if update was successful, False otherwise
        """
        user_info = self.db.get_user_info(agent_id) or dict(self.default_template)
        user_info[field] = value
        return self.db.set_user_info(agent_id, user_info)

    def get_user_info_text(self, agent_id: str) -> str:
        """Get user information for a given agent_id in a formatted text string"""
        user_info = self.get_user_info(agent_id)
        return str(user_info)

    def initialize_user_info(self, agent_id: str) -> None:
        """Initialize user info for a new agent_id using the default template if not present."""
        if self.db.get_user_info(agent_id) is None:
            self.db.set_user_info(agent_id, dict(self.default_template))
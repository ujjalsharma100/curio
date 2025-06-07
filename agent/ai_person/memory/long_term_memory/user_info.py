import json
import os
from typing import Dict, Optional

class UserInfo:
    def __init__(self):
        # Instance variables for user information
        self.name: str = ""
        self.interests: str = ""
        self.job: str = ""
        self.info: str = ""
        
        self.json_file = os.path.join(os.path.dirname(__file__), "user_info.json")
        self.load_from_json()
    
    def load_from_json(self) -> None:
        """Load user information from JSON file if it exists, otherwise create with default values"""
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, 'r') as f:
                    data = json.load(f)
                    self.name = data.get('name', self.name)
                    self.interests = data.get('interests', self.interests)
                    self.job = data.get('job', self.job)
                    self.info = data.get('info', self.info)
            except json.JSONDecodeError:
                print("Error reading JSON file, using default values")
        else:
            self.save_to_json()
    
    def save_to_json(self) -> None:
        """Save current user information to JSON file"""
        data = {
            'name': self.name,
            'interests': self.interests,
            'job': self.job,
            'info': self.info
        }
        try:
            with open(self.json_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving to JSON: {e}")
    
    def get_user_info(self) -> Dict[str, str]:
        """Get all user information as a dictionary"""
        self.load_from_json()
        return {
            'name': self.name,
            'interests': self.interests,
            'job': self.job,
            'info': self.info
        }
    
    def update_user_info(self, field: str, value: str) -> bool:
        """Update a specific field of user information
        
        Args:
            field: The field to update (name, interests, job, or info)
            value: The new value for the field
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        self.load_from_json()
        if not hasattr(self, field):
            return False
            
        setattr(self, field, value)
        self.save_to_json()
        return True
    
    def get_user_info_text(self) -> str:
        """Get user information in a formatted text string"""
        self.load_from_json()
        user_info = self.get_user_info()
        return str(user_info)
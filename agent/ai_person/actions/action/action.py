from abc import ABC, abstractmethod
from typing import Any

class Action(ABC):
    """Base class for all actions."""
    
    def __init__(self, description: str, name: str, args: dict[str, str]):
        self.description = description
        self.name = name
        self.args = args
    
    @abstractmethod
    def execute(self, agent_id: str, args: dict[str, Any]):
        """Execute the action for a given agent and return the result."""
        pass
    

    def get_action_name(self) -> str:
        """Return the name of the action."""
        self.name

    def get_action_descrption(self) -> str:
        return self.description
    
    def get_action_detail(self) -> str:

        arguments_str = "\n".join([f"{arg_key}: {arg_description}" for arg_key, arg_description in self.args.items()])
        detail = f"""
        Action Name: {self.name},
        Action Description: {self.description},
        Action Arguments: [
            {arguments_str}
        ]
        """

        return detail
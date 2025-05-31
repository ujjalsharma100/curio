from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Type
from datetime import datetime
from .action import Action
from .action.implementations import (
    SayTextAction,
    FetchLatestAINewsAction,
    FetchNewsDetailsAction,
    AskQuestionAction
)

class Actions:
    """Class to manage available actions and their execution."""
    
    def __init__(self):
        self.available_actions: List[Action] = [
            SayTextAction(),
            FetchLatestAINewsAction(),
            FetchNewsDetailsAction(),
            AskQuestionAction()
        ]
        

    def execute_action(self, action_name: str, action_args: dict[str, Any]):
        """
        Execute an action by its name with the provided arguments.

        Args:
            action_name (str): The name of the action to execute.
            action_args (dict[str, Any]): Arguments to pass to the action.

        Returns:
            Any: The result of the action's execution, or None if not found.
        """
        for action in self.available_actions:
            if action.name == action_name:
                try:
                    action.execute(action_args)
                except Exception as e:
                    print(f"Error executing action '{action_name}': {e}")
                    return None
        print(f"Action '{action_name}' not found among available actions.")

    def get_all_actions_details(self):
        details = []
        for action in self.available_actions:
            details.append(action.get_action_detail())
        return details
    

    def get_all_available_actions_prompt(self) -> str:
        details = self.get_all_actions_details()
        action_details = []
        for idx, detail in enumerate(details, 1):
            action_details.append(f"{idx}. {detail}")

        all_action_details = "\n".join(action_details)
        final_text = f"""
        You are able to perform a set of actions. 
        The details about all the actions that you can perform is listed here. 
        {all_action_details}
        """

        return final_text
    


    
    
    
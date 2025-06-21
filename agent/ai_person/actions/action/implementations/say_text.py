from typing import Any
from ..action import Action
from ....memory import Memory
from .curio_chat_messenger import send_agent_message

class SayTextAction(Action):
    
    def __init__(self, 
                description = "Send message to the human. This action is if you want to communicate some information to the human.", 
                name = "say_text",
                args = {
                    "message": "The message to be sent to the human."
                }):
        self.memory = Memory()
        super().__init__(description, name, args)

    def execute(self, agent_id: str, args: dict[str, Any]):
        try:
            message = args['message']
            self.say_text(agent_id, message)
            agent_dialouge = f"You: {message}"
            self.memory.add_dialogue_to_current_converstaion(agent_id, agent_dialouge)
        except Exception as e:
            print(e)
    
    def say_text(self, agent_id, message):
        send_agent_message(agent_id, message)
    
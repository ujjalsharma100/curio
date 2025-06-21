from typing import Any
from ..action import Action
from ....memory import Memory
from .curio_chat_messenger import send_agent_message

class AskQuestionAction(Action):
    
    def __init__(self,
                description = "Ask a question to the human to get more clarity. This action sends a question to the human.", 
                name = "ask_question",
                args = {
                    "question": "The question to ask the human."
                }):
        self.memory = Memory()
        super().__init__(description=description, name=name, args=args)
    
    def execute(self, agent_id: str, args: dict[str, Any]):
        try:
            question = args['question']
            self.ask_question(agent_id, question)
            agent_dialouge = f"You: {question}"
            self.memory.add_dialogue_to_current_converstaion(agent_id, agent_dialouge)
        except Exception as e:
            print(e)

    def ask_question(self, agent_id, question: str):
        send_agent_message(agent_id, question)
        
    

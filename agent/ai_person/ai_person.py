from .memory import Memory
from .personality import Personality
from .identity import Identity
from .purpose import Purpose
from .actions import Actions
from .llm_service import get_response_from_llm
import json

class AiPerson:
    def __init__(self):
        self.identity = Identity()
        self.personality = Personality()
        self.purpose = Purpose()
        self.memory = Memory()
        self.actions = Actions()
    

    def hear_text(self, text: str) -> None:
        try:
            print(text)
            user_dialouge = f"Human: {text}"
            self.memory.add_dialogue_to_current_converstaion(user_dialouge)


            response_structure = {
                "action_name": "<Name of the Action from the list of actions>",
                "action_args": {
                    "<argument key>": "<argument_value>"
                }
            }

            response_structure_str = json.dumps(response_structure)

            prompt = f"""
            - Indentity:
            {self.identity.get_indentity_prompt()}
            - Purpose:
            {self.purpose.get_purpose_prompt()}
            - Personality:
            {self.personality.get_personality_prompt_text()}
            - Details about Human:
            {self.memory.get_information_about_the_human_prompt()}
            - Available Actions:
            {self.actions.get_all_available_actions_prompt()}
            - Current Converstaion
            {self.memory.get_current_conversation_prompt()}
            - Expected Resonse
            Base on the current converstaion, respond what should be the next action from the available actions.
            Analyze and Understand the most recent ask/want from human from the converstaion, not some previous ask.
            The past converstational history is for better understanding of the context.
            Incorporate the details and information provided in each section.
            Response should be a json string of the following structure:
            {response_structure_str}
            The response should only be the action json string.
            """

            response_from_llm = get_response_from_llm(prompt=prompt)

            response_json = json.loads(response_from_llm)
            print(response_json)

            action_name = response_json.get('action_name', 'default_action')
            action_args = response_json.get("action_args", {})

            self.actions.execute_action(action_name=action_name, action_args=action_args)



        except Exception as e:
            print(e)

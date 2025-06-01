from typing import Any
from ..action import Action
from .ai_news_fetcher import get_ai_updates
from ....memory import Memory
from ....identity import Identity
from ....purpose import Purpose
from ....personality import Personality
from ....llm_service import get_response_from_llm
from .curio_chat_messenger import send_agent_message
import json


class FetchLatestAINewsAction(Action):

    def __init__(self, description = "Get latest AI news from web sources. This action is fetches latest AI updates and sends those updates to the human. This is the action to perform when use asks for updates. This action collects information from web and also communicates them to the user", 
                name = "fetch_ai_news",
                args = {}):
        self.memory = Memory()
        self.identity = Identity()
        self.personality = Personality()
        self.purpose = Purpose()
        super().__init__(description, name, args)

    def execute(self, args: dict[str, Any]):
        try:
            self.fetch_ai_news_and_send()
        except Exception as e:
            print(e)
    
    def fetch_ai_news_and_send(self):

        ai_updates = get_ai_updates()
        ai_updates_string = json.dumps(ai_updates)
    
        prompt = f"""
        - Indentity:
        {self.identity.get_indentity_prompt()}
        - Purpose:
        {self.purpose.get_purpose_prompt()}
        - Personality:
        {self.personality.get_personality_prompt_text()}
        - Details about Human:
        {self.memory.get_information_about_the_human_prompt()}
        - Current Converstaion:
        {self.memory.get_current_conversation_prompt()}
        - AI news information:
        {ai_updates_string}
        - Expected Resonse
        Based on the current converstation, all the context and AI news information.
        You have to send the the human the Ai news information that would be relevant to the human.
        If AI news information is empty, communicate that to the human that theres nothing new.
        The response should the text you would be sending to the human. 
        The text should also contain insights on why it would be relevant to the humnan and improvise on it a bit.
        The responses should only be the text to be send to the human. Include nothing else.
        """

        response_text = get_response_from_llm(prompt=prompt)
        send_agent_message(response_text)
        agent_dialogue = f"You: {response_text}"
        self.memory.add_dialogue_to_current_converstaion(agent_dialogue)







    
from typing import Any
from ..action import Action
from .ai_news_fetcher import get_fetched_ai_news
from ....memory import Memory
from ....identity import Identity
from ....purpose import Purpose
from ....personality import Personality
from ....llm_service import get_response_from_llm
from .curio_chat_messenger import send_agent_message
import json

class FetchNewsDetailsAction(Action):
    
    def __init__(self, description = "Get details and extra information regarding some update when the human wants it and send it to the human. This action searches the already fetched information previously and also sends/communicates the information to the human.", 
                name = "fetch_news_details",
                args = {}):
        self.memory = Memory()
        self.identity = Identity()
        self.purpose = Purpose()
        self.personality = Personality()
        super().__init__(description, name, args)

    def execute(self, args: dict[str, Any]):
        try:
            self.fetch_news_details()
        except Exception as e:
            print(e)
    
    def fetch_news_details(self):
        fetched_ai_news = get_fetched_ai_news()
        fetched_ai_news_string = json.dumps(fetched_ai_news)

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
        {fetched_ai_news_string}
        - Expected Resonse
        Based on the current converstation, all the context and AI news information.
        You have the send a response to the human about what detail or answer the human was looking for.
        The AI news information contains a lot of details, some extra information, but you have to only inlclude the section, or news item that the human is looking for. 
        No need to include updates about other items. Understand what the human wants to know and include those things only.
        The response should the text you would be sending to the human.
        The responses should only be the text to be send to the human. Include nothing else.
        """

        response_text = get_response_from_llm(prompt=prompt)
        send_agent_message(response_text)
        agent_dialogue = f"You: {response_text}"
        self.memory.add_dialogue_to_current_converstaion(agent_dialogue)

        print('ai')
    
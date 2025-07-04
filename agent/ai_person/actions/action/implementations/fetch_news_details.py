from typing import Any
from ..action import Action
from ....memory import Memory
from ....identity import Identity
from ....purpose import Purpose
from ....personality import Personality
from ....llm_service import get_response_from_llm
from .curio_chat_messenger import send_agent_message
from .logging_setup import setup_action_logging
import json

class FetchNewsDetailsAction(Action):
    
    def __init__(self, description = "Get details and extra information regarding some update when the human wants it and send it to the human. This action searches the already fetched information previously and also sends/communicates the information to the human.", 
                name = "fetch_news_details",
                args = {
                    "query": "The query to search with to get the relevant article"
                }):
        self.logger = setup_action_logging("fetch_news_details")
        self.logger.info("Initializing FetchNewsDetailsAction")
        self.memory = Memory()
        self.identity = Identity()
        self.purpose = Purpose()
        self.personality = Personality()
        super().__init__(description, name, args)
        self.logger.info("FetchNewsDetailsAction initialization complete")

    def execute(self, agent_id: str, args: dict[str, Any]):
        try:
            self.logger.info(f"Starting fetch_news_details action execution for agent_id: {agent_id}")
            query = args["query"]
            self.logger.info(f"Query received for agent_id {agent_id}: {query}")
            self.fetch_news_details(query=query, agent_id=agent_id)
            self.logger.info(f"fetch_news_details action execution completed successfully for agent_id: {agent_id}")
        except Exception as e:
            self.logger.error(f"Error in fetch_news_details action execution for agent_id {agent_id}: {str(e)}", exc_info=True)
            print(e)
    
    def fetch_news_details(self, query: str, agent_id: str):
        self.logger.info(f"Starting news details search for query: {query} for agent_id: {agent_id}")

        self.logger.debug(f"Searching for relevant news in memory for agent_id: {agent_id}")
        fetched_ai_news = self.memory.search_relevant_news(agent_id=agent_id, query=query, top_k=1)
        self.logger.info(f"Found {len(fetched_ai_news)} relevant news items for agent_id: {agent_id}")
        
        if fetched_ai_news:
            for i, news_item in enumerate(fetched_ai_news):
                self.logger.debug(f"News item {i+1} for agent_id {agent_id}: {news_item.get('title', 'No title')} from {news_item.get('source', 'Unknown source')}")
        else:
            self.logger.warning(f"No relevant news items found for the query for agent_id: {agent_id}")
            
        fetched_ai_news_string = json.dumps(fetched_ai_news)
        self.logger.debug(f"News items JSON string length for agent_id {agent_id}: {len(fetched_ai_news_string)} characters")

        self.logger.debug(f"Constructing prompt for LLM for agent_id: {agent_id}")
        prompt = f"""
        - Indentity:
        {self.identity.get_indentity_prompt(agent_id) if hasattr(self.identity, 'get_indentity_prompt') and 'agent_id' in self.identity.get_indentity_prompt.__code__.co_varnames else self.identity.get_indentity_prompt()}
        - Purpose:
        {self.purpose.get_purpose_prompt(agent_id) if hasattr(self.purpose, 'get_purpose_prompt') and 'agent_id' in self.purpose.get_purpose_prompt.__code__.co_varnames else self.purpose.get_purpose_prompt()}
        - Personality:
        {self.personality.get_personality_prompt_text(agent_id)}
        - Details about Human:
        {self.memory.get_information_about_the_human_prompt(agent_id)}
        - Current Converstaion:
        {self.memory.get_current_conversation_prompt(agent_id)}
        - AI news information:
        {fetched_ai_news_string}
        - Expected Resonse
        Based on the current converstation, all the context and AI news information.
        Understand the most recent want from human from the converstaion, not some previous ask. 
        You have the send a response to the human about what detail or answer the human was looking for.
        The AI news information contains a lot of details, some extra information, but you have to only inlclude the section, or news item that the human is looking for. 
        No need to include updates about other items. Understand what the human wants to know and include those things only.
        The response should the text you would be sending to the human.
        The responses should only be the text to be send to the human. Include nothing else.
        """
        self.logger.debug(f"Prompt length for agent_id {agent_id}: {len(prompt)} characters")
        self.logger.info(f"Complete prompt for LLM for agent_id {agent_id}:\n{prompt}")

        self.logger.info(f"Calling LLM service for response generation for agent_id: {agent_id}")
        response_text = get_response_from_llm(prompt=prompt)
        self.logger.info(f"Received response from LLM for agent_id {agent_id}, length: {len(str(response_text))} characters")
        self.logger.debug(f"LLM response for agent_id {agent_id}: {response_text}")
        
        # Null and type checks for response_text
        if not response_text or not isinstance(response_text, str):
            self.logger.error(f"Invalid response from LLM: {response_text}")
            print("Error: Invalid response from LLM.")
            return
        
        self.logger.info(f"Sending agent message to human for agent_id: {agent_id}")
        send_agent_message(agent_id, response_text)
        agent_dialogue = f"You: {response_text}"
        self.memory.add_dialogue_to_current_converstaion(agent_id, agent_dialogue)
        self.logger.debug(f"Added agent dialogue to conversation memory for agent_id: {agent_id}")

        self.logger.info(f"News details fetching and sending process completed for agent_id: {agent_id}")
    
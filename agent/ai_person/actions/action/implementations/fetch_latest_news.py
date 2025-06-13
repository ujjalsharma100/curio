from typing import Any
from ..action import Action
from . import ai_news_fetcher
from ....memory import Memory
from ....identity import Identity
from ....purpose import Purpose
from ....personality import Personality
from ....llm_service import get_response_from_llm
from .curio_chat_messenger import send_agent_message
from .logging_setup import setup_action_logging
import json


class FetchLatestAINewsAction(Action):

    def __init__(self, description = "Get latest AI news from web sources. This action is fetches latest AI updates and sends those updates to the human. This is the action to perform when use asks for updates. This action collects information from web and also communicates them to the user", 
                name = "fetch_ai_news",
                args = {}):
        self.logger = setup_action_logging("fetch_latest_news")
        self.logger.info("Initializing FetchLatestAINewsAction")
        self.memory = Memory()
        self.identity = Identity()
        self.personality = Personality()
        self.purpose = Purpose()
        super().__init__(description, name, args)
        self.logger.info("FetchLatestAINewsAction initialization complete")

    def execute(self, args: dict[str, Any]):
        try:
            self.logger.info("Starting fetch_latest_news action execution")
            self.fetch_ai_news_and_send()
            self.logger.info("fetch_latest_news action execution completed successfully")
        except Exception as e:
            self.logger.error(f"Error in fetch_latest_news action execution: {str(e)}", exc_info=True)
            print(e)
    
    def fetch_ai_news_and_send(self):
        self.logger.info("Starting AI news fetching process")

        self.logger.debug("Calling ai_news_fetcher.get_ai_updates()")
        ai_updates = ai_news_fetcher.get_ai_updates()
        self.logger.info(f"Retrieved {len(ai_updates)} AI updates from sources")
        
        final_ai_updates = []
        self.logger.debug("Processing AI updates and filtering duplicates")
        for i, ai_update in enumerate(ai_updates):
            self.logger.debug(f"Processing update {i+1}/{len(ai_updates)}: {ai_update.get('title', 'No title')}")
            
            if ai_update['link'] == "" or ai_update['link'] is None:
                self.logger.debug(f"Skipping update {i+1}: Empty or None link")
                continue
                
            if self.memory.check_link_exists(ai_update['link']):
                self.logger.debug(f"Skipping update {i+1}: Link already exists in memory")
                continue
                
            self.logger.debug(f"Fetching content for update {i+1}: {ai_update['link']}")
            content = ai_news_fetcher.fetch_article_content(ai_update)
            if content:
                ai_update["content"] = content
                final_ai_updates.append(ai_update)
                self.logger.debug(f"Successfully added update {i+1} to final updates")
            else:
                self.logger.debug(f"No content retrieved for update {i+1}")
    
        self.logger.info(f"Final AI updates after processing: {len(final_ai_updates)}")
        ai_updates_string = json.dumps(final_ai_updates)
        self.logger.debug(f"AI updates JSON string length: {len(ai_updates_string)} characters")
    
        self.logger.debug("Constructing prompt for LLM")
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
        self.logger.debug(f"Prompt length: {len(prompt)} characters")
        self.logger.info(f"Complete prompt for LLM:\n{prompt}")

        self.logger.info("Calling LLM service for response generation")
        response_text = get_response_from_llm(prompt=prompt)
        self.logger.info(f"Received response from LLM, length: {len(response_text)} characters")
        self.logger.debug(f"LLM response: {response_text}")
        
        self.logger.info("Sending agent message to human")
        send_agent_message(response_text)
        agent_dialogue = f"You: {response_text}"
        self.memory.add_dialogue_to_current_converstaion(agent_dialogue)
        self.logger.debug("Added agent dialogue to conversation memory")

        self.logger.info(f"Saving {len(final_ai_updates)} news items to memory")
        for i, update in enumerate(final_ai_updates):
            try:
                self.memory.save_news_item(update)
                self.logger.debug(f"Successfully saved news item {i+1}: {update.get('title', 'No title')}")
            except Exception as e:
                self.logger.error(f"Error saving news item {i+1}: {str(e)}")
        
        self.logger.info("AI news fetching and sending process completed")
        







    
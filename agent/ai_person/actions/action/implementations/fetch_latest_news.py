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

    def execute(self, agent_id: str, args: dict[str, Any]):
        try:
            self.logger.info("Starting fetch_latest_news action execution")
            self.fetch_ai_news_and_send(agent_id)
            self.logger.info("fetch_latest_news action execution completed successfully")
        except Exception as e:
            self.logger.error(f"Error in fetch_latest_news action execution: {str(e)}", exc_info=True)
            print(e)
    
    def fetch_ai_news_and_send(self, agent_id: str):
        self.logger.info("Starting AI news fetching process")

        self.logger.debug("Calling ai_news_fetcher.get_ai_updates()")
        ai_updates = ai_news_fetcher.get_ai_updates()
        self.logger.info(f"Retrieved {len(ai_updates)} AI updates from sources")
        
        final_ai_updates = []  # All news to send to user
        to_fetch_and_save = []  # News not in DB, need to fetch content and save
        news_id_map = {}  # Map link to news_id for later marking

        for i, ai_update in enumerate(ai_updates):
            self.logger.debug(f"Processing update {i+1}/{len(ai_updates)}: {ai_update.get('title', 'No title')}")
            link = ai_update.get('link', '')
            if not link:
                self.logger.debug(f"Skipping update {i+1}: Empty or None link")
                continue
            news_id = self.memory.check_link_exists(agent_id, link)
            if news_id:
                news_id_map[link] = news_id
                # Check if processed by this agent
                if self.memory.long_term_memory.news_db.has_agent_processed_news(agent_id, news_id):
                    self.logger.debug(f"Skipping update {i+1}: Already processed by agent {agent_id}")
                    continue
                # Not processed by this agent, fetch from memory and include in final_ai_updates
                news_item = self.memory.get_news_item(agent_id, news_id)
                if news_item:
                    final_ai_updates.append(news_item)
                else:
                    self.logger.error(f"Could not fetch news item for news_id {news_id}")
            else:
                # Not in DB, need to fetch content and save
                to_fetch_and_save.append(ai_update)
        
        # Fetch content for new items and add to final_ai_updates
        for ai_update in to_fetch_and_save:
            self.logger.debug(f"Fetching content for new update: {ai_update['link']}")
            content = ai_news_fetcher.fetch_article_content(ai_update)
            if content:
                ai_update['content'] = content
                final_ai_updates.append(ai_update)
            else:
                self.logger.debug(f"No content retrieved for new update: {ai_update['link']}")
        
        self.logger.info(f"Final AI updates after processing: {len(final_ai_updates)}")
        ai_updates_string = json.dumps(final_ai_updates)
        self.logger.debug(f"AI updates JSON string length: {len(ai_updates_string)} characters")
    
        self.logger.debug("Constructing prompt for LLM")
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
        send_agent_message(agent_id, response_text)
        agent_dialogue = f"You: {response_text}"
        self.memory.add_dialogue_to_current_converstaion(agent_id, agent_dialogue)
        self.logger.debug("Added agent dialogue to conversation memory")

        # Save only new items to DB, get their news_id
        self.logger.info(f"Saving {len(to_fetch_and_save)} new news items to memory")
        for i, update in enumerate(to_fetch_and_save):
            try:
                news_id = self.memory.save_news_item(agent_id, update)
                if news_id:
                    update['news_id'] = news_id
                    news_id_map[update['link']] = news_id
                    self.logger.debug(f"Successfully saved news item {i+1}: {update.get('title', 'No title')}")
                else:
                    self.logger.error(f"Failed to save news item {i+1}: {update.get('title', 'No title')}")
            except Exception as e:
                self.logger.error(f"Error saving news item {i+1}: {str(e)}")

        # Mark all items in final_ai_updates as processed for this agent
        self.logger.info(f"Marking {len(final_ai_updates)} news items as processed for agent {agent_id}")
        for i, update in enumerate(final_ai_updates):
            news_id = update.get('news_id') or news_id_map.get(update.get('link'))
            if news_id:
                try:
                    self.memory.long_term_memory.news_db.mark_news_processed_by_agent(agent_id, news_id)
                    self.logger.debug(f"Marked news item {i+1} as processed: {update.get('title', 'No title')}")
                except Exception as e:
                    self.logger.error(f"Error marking news item {i+1} as processed: {str(e)}")
            else:
                self.logger.error(f"No news_id found for news item {i+1}: {update.get('title', 'No title')}")

        self.logger.info("AI news fetching and sending process completed")
        







    
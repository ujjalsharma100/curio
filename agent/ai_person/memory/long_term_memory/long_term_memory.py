from .user_info import UserInfo
from .news_vector_db import NewsVectorDB
from .news_db import NewsDB
from .conversation_db import ConversationDB
from typing import Dict, Any, Optional, List
import logging
import os
from datetime import datetime
import uuid

# Setup logging for long term memory
def setup_memory_logging():
    """Setup logging for the long term memory module."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, f"long_term_memory_{datetime.now().strftime('%Y%m%d')}.log")
    
    # Create logger
    logger = logging.getLogger("ai_person.memory.long_term_memory")
    logger.setLevel(logging.DEBUG)
    
    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Initialize logger
logger = setup_memory_logging()

class LongTermMemory:

    def __init__(self):
        logger.info("Initializing LongTermMemory")
        self.user_info = UserInfo()
        self.news_vector_db = NewsVectorDB()
        self.news_db = NewsDB()
        self.conversation_db = ConversationDB()
        logger.info("LongTermMemory initialization complete")

    def get_user_information_text(self, agent_id: str) -> str:
        return self.user_info.get_user_info_text(agent_id)
    
    def update_user_information(self, agent_id: str, field, value):
        logger.debug(f"Updating user information: {field} = {value}")
        return self.user_info.update_user_info(agent_id, field=field, value=value)
    
    def save_news_item(self, agent_id: str, news_item: Dict[str, Any]) -> Optional[str]:
        """Save a news item to both vector database and SQLite database.
        
        Args:
            agent_id: ID of the agent
            news_item: Dictionary containing news item data with keys:
                      title, summary, content, link, source, published
        
        Returns:
            Optional[str]: The ID of the saved news item if successful, None otherwise
        """
        logger.info(f"Saving news item: {news_item.get('title', 'No title')}")
        try:
            # First save to vector database to get the news_id
            logger.debug("Saving to vector database")
            news_id = self.news_vector_db.add_news_item(news_item)
            logger.debug(f"Generated news_id: {news_id}")
            
            # Then save full details to SQLite
            logger.debug("Saving to SQLite database")
            if self.news_db.save_news_item(news_id, news_item):
                logger.info(f"Successfully saved news item with ID: {news_id}")
                return news_id
            else:
                logger.error("Failed to save news item to SQLite database")
                return None
        except Exception as e:
            logger.error(f"Error saving news item: {str(e)}", exc_info=True)
            print(f"Error saving news item: {str(e)}")
            return None
        
    
    def get_news_item(self, agent_id: str, news_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a news item from the SQLite database.
        
        Args:
            agent_id: ID of the agent
            news_id: ID of the news item to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: News item data if found, None otherwise
        """
        logger.debug(f"Retrieving news item with ID: {news_id}")
        news_item = self.news_db.get_news_item(news_id)
        if news_item:
            logger.debug(f"Successfully retrieved news item: {news_item.get('title', 'No title')}")
        else:
            logger.warning(f"No news item found with ID: {news_id}")
        return news_item
    
    def search_relevant_news(self, agent_id: str, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for news items relevant to the query and return their full details, filtered by agent_id."""
        logger.info(f"Searching for relevant news with query: '{query}', top_k: {top_k}, agent_id: {agent_id}")
        try:
            # First get relevant news IDs from vector database
            logger.debug("Searching vector database for relevant news IDs")
            news_ids = self.news_vector_db.search_news(query, top_k=top_k)
            logger.debug(f"Found {len(news_ids)} relevant news IDs: {news_ids}")

            # Filter news_ids to only those processed by this agent
            processed_news_ids = set(self.news_db.get_news_ids_processed_by_agent(agent_id))
            news_ids = [nid for nid in news_ids if nid in processed_news_ids]
            logger.debug(f"Filtered news_ids for agent_id {agent_id}: {news_ids}")

            # Then get full details for each news item from SQLite
            news_items = []
            for i, news_id in enumerate(news_ids):
                logger.debug(f"Retrieving details for news item {i+1}/{len(news_ids)}: {news_id}")
                news_item = self.get_news_item(agent_id, news_id)
                if news_item:
                    news_items.append(news_item)
                    logger.debug(f"Added news item to results: {news_item.get('title', 'No title')}")
                else:
                    logger.warning(f"Could not retrieve details for news_id: {news_id}")

            logger.info(f"Search completed, returning {len(news_items)} news items")
            return news_items
        except Exception as e:
            logger.error(f"Error searching relevant news: {str(e)}", exc_info=True)
            print(f"Error searching relevant news: {str(e)}")
            return []
    
    def check_link_exists(self, agent_id: str, link: str) -> Optional[str]:
        """Check if a news link already exists in the long-term memory.
        
        Args:
            agent_id: ID of the agent
            link: The URL link to check for existence
            
        Returns:
            Optional[str]: The news_id if the link exists in the database, None otherwise
        """
        logger.debug(f"Checking if link exists: {link}")
        try:
            news_id = self.news_db.link_exists(link)
            if news_id:
                logger.debug(f"Link already exists in database: {link}, news_id: {news_id}")
                return news_id
            else:
                logger.debug(f"Link does not exist in database: {link}")
                return None
        except Exception as e:
            logger.error(f"Error checking link existence in long-term memory: {str(e)}", exc_info=True)
            print(f"Error checking link existence in long-term memory: {str(e)}")
            return None
    
    def save_dialogue(self, agent_id: str, dialogue: str) -> Optional[str]:
        """Save a conversation dialogue to the conversation database.
        
        Args:
            agent_id: ID of the agent
            dialogue: The conversation dialogue text to save
            
        Returns:
            Optional[str]: The ID of the saved conversation if successful, None otherwise
        """
        logger.info(f"Saving dialogue to conversation database")
        logger.debug(f"Dialogue length: {len(dialogue)} characters")
        try:
            # Generate a unique conversation ID
            conversation_id = str(uuid.uuid4())
            logger.debug(f"Generated conversation_id: {conversation_id}")
            
            # Save to conversation database
            if self.conversation_db.save_conversation(agent_id, conversation_id, dialogue):
                logger.info(f"Successfully saved dialogue with ID: {conversation_id}")
                return conversation_id
            else:
                logger.error("Failed to save dialogue to conversation database")
                return None
        except Exception as e:
            logger.error(f"Error saving dialogue: {str(e)}", exc_info=True)
            print(f"Error saving dialogue: {str(e)}")
            return None
    
    def get_conversation(self, agent_id: str, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a conversation from the conversation database.
        
        Args:
            agent_id: ID of the agent
            conversation_id: ID of the conversation to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Conversation data if found, None otherwise
        """
        logger.debug(f"Retrieving conversation with ID: {conversation_id}")
        conversation = self.conversation_db.get_conversation(agent_id, conversation_id)
        if conversation:
            logger.debug(f"Successfully retrieved conversation: {conversation_id}")
        else:
            logger.warning(f"No conversation found with ID: {conversation_id}")
        return conversation
    
    def get_all_conversations(self, agent_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve all conversations from the conversation database.
        
        Args:
            agent_id: ID of the agent
            limit: Optional limit on the number of conversations to return
            
        Returns:
            List[Dict[str, Any]]: List of conversation data
        """
        logger.info(f"Retrieving all conversations for agent_id={agent_id}, limit: {limit}")
        try:
            conversations = self.conversation_db.get_all_conversations(agent_id, limit=limit)
            logger.info(f"Retrieved {len(conversations)} conversations")
            return conversations
        except Exception as e:
            logger.error(f"Error retrieving conversations: {str(e)}", exc_info=True)
            print(f"Error retrieving conversations: {str(e)}")
            return []
    
    
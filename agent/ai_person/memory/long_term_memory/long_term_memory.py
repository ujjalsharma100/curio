from .user_info import UserInfo
from .news_vector_db import NewsVectorDB
from .news_db import NewsDB
from typing import Dict, Any, Optional, List
import logging
import os
from datetime import datetime

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
        logger.info("LongTermMemory initialization complete")

    def get_user_information_text(self) -> str:
        return self.user_info.get_user_info_text()
    
    def update_user_information(self, field, value):
        logger.debug(f"Updating user information: {field} = {value}")
        return self.user_info.update_user_info(field=field, value=value)
    
    def save_news_item(self, news_item: Dict[str, Any]) -> Optional[str]:
        """Save a news item to both vector database and SQLite database.
        
        Args:
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
        
    
    def get_news_item(self, news_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a news item from the SQLite database.
        
        Args:
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
    
    def search_relevant_news(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for news items relevant to the query and return their full details.
        
        Args:
            query: Search query string to find relevant news items
            top_k: Number of most relevant results to return (default: 3)
            
        Returns:
            List[Dict[str, Any]]: List of news items with their full details, ordered by relevance.
                                 Each news item contains: news_id, title, summary, content, 
                                 link, source, published_at, and created_at.
        """
        logger.info(f"Searching for relevant news with query: '{query}', top_k: {top_k}")
        try:
            # First get relevant news IDs from vector database
            logger.debug("Searching vector database for relevant news IDs")
            news_ids = self.news_vector_db.search_news(query, top_k=top_k)
            logger.debug(f"Found {len(news_ids)} relevant news IDs: {news_ids}")
            
            # Then get full details for each news item from SQLite
            news_items = []
            for i, news_id in enumerate(news_ids):
                logger.debug(f"Retrieving details for news item {i+1}/{len(news_ids)}: {news_id}")
                news_item = self.get_news_item(news_id)
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
    
    def check_link_exists(self, link: str) -> bool:
        """Check if a news link already exists in the long-term memory.
        
        Args:
            link: The URL link to check for existence
            
        Returns:
            bool: True if the link exists in the database, False otherwise
        """
        logger.debug(f"Checking if link exists: {link}")
        try:
            exists = self.news_db.link_exists(link)
            if exists:
                logger.debug(f"Link already exists in database: {link}")
            else:
                logger.debug(f"Link does not exist in database: {link}")
            return exists
        except Exception as e:
            logger.error(f"Error checking link existence in long-term memory: {str(e)}", exc_info=True)
            print(f"Error checking link existence in long-term memory: {str(e)}")
            return False
    
    
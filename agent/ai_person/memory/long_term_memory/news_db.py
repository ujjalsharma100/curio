import sqlite3
import os
from typing import Dict, Any, Optional
from datetime import datetime
import logging

# Setup logging for news database
def setup_news_db_logging():
    """Setup logging for the news database module."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, f"news_db_{datetime.now().strftime('%Y%m%d')}.log")
    
    # Create logger
    logger = logging.getLogger("ai_person.memory.news_db")
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
logger = setup_news_db_logging()

class NewsDB:
    def __init__(self, db_path: str = "news.db"):
        """Initialize the news SQLite database.
        
        Args:
            db_path: Path to the SQLite database file
        """
        logger.info("Initializing NewsDB")
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Create full path to database file
        self.db_path = os.path.join(current_dir, db_path)
        logger.debug(f"SQLite database path: {self.db_path}")
        self._create_tables()
        logger.info("NewsDB initialization complete")
    
    def _create_tables(self):
        """Create necessary database tables if they don't exist"""
        logger.debug("Creating database tables if they don't exist")
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS news_items (
                        news_id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        summary TEXT,
                        content TEXT NOT NULL,
                        link TEXT,
                        source TEXT,
                        published_at TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                # New table for agent-news mapping
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS agent_news_processed (
                        agent_id TEXT NOT NULL,
                        news_id TEXT NOT NULL,
                        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (agent_id, news_id),
                        FOREIGN KEY (news_id) REFERENCES news_items(news_id)
                    )
                ''')
                conn.commit()
                logger.debug("Database tables created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}", exc_info=True)
            raise
    
    def save_news_item(self, news_id: str, news_item: Dict[str, Any]) -> bool:
        """Save a news item to the SQLite database.
        
        Args:
            news_id: Unique identifier for the news item
            news_item: Dictionary containing news item data
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        logger.info(f"Saving news item to SQLite database: {news_item.get('title', 'No title')}")
        logger.debug(f"News ID: {news_id}")
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO news_items 
                    (news_id, title, summary, content, link, source, published_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    news_id,
                    news_item.get('title', ''),
                    news_item.get('summary', ''),
                    news_item.get('content', ''),
                    news_item.get('link', ''),
                    news_item.get('source', ''),
                    news_item.get('published', '')  # Store the published date string as is
                ))
                conn.commit()
                logger.info(f"Successfully saved news item to SQLite database: {news_item.get('title', 'No title')}")
                return True
        except Exception as e:
            logger.error(f"Error saving news item to SQLite: {str(e)}", exc_info=True)
            print(f"Error saving news item to SQLite: {str(e)}")
            return False
    
    def get_news_item(self, news_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a news item from the database.
        
        Args:
            news_id: ID of the news item to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: News item data if found, None otherwise
        """
        logger.debug(f"Retrieving news item from SQLite database: {news_id}")
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT news_id, title, summary, content, link, source, published_at, created_at
                    FROM news_items
                    WHERE news_id = ?
                ''', (news_id,))
                row = cursor.fetchone()
                
                if row:
                    news_item = {
                        'news_id': row[0],
                        'title': row[1],
                        'summary': row[2],
                        'content': row[3],
                        'link': row[4],
                        'source': row[5],
                        'published_at': row[6],
                        'created_at': row[7]
                    }
                    logger.debug(f"Successfully retrieved news item: {news_item.get('title', 'No title')}")
                    return news_item
                else:
                    logger.warning(f"No news item found with ID: {news_id}")
                    return None
        except Exception as e:
            logger.error(f"Error retrieving news item from SQLite: {str(e)}", exc_info=True)
            print(f"Error retrieving news item: {str(e)}")
            return None

    def link_exists(self, link: str) -> Optional[str]:
        """Check if a news link already exists in the database.
        
        Args:
            link: The URL link to check for existence
            
        Returns:
            Optional[str]: The news_id if the link exists in the database, None otherwise
        """
        logger.debug(f"Checking if link exists in SQLite database: {link}")
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT news_id
                    FROM news_items
                    WHERE link = ?
                ''', (link,))
                row = cursor.fetchone()
                if row:
                    logger.debug(f"Link already exists in SQLite database: {link}, news_id: {row[0]}")
                    return row[0]
                else:
                    logger.debug(f"Link does not exist in SQLite database: {link}")
                    return None
        except Exception as e:
            logger.error(f"Error checking link existence in SQLite: {str(e)}", exc_info=True)
            print(f"Error checking link existence: {str(e)}")
            return None

    def mark_news_processed_by_agent(self, agent_id: str, news_id: str) -> bool:
        """Mark a news item as processed by a specific agent."""
        logger.info(f"Marking news_id {news_id} as processed by agent_id {agent_id}")
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO agent_news_processed (agent_id, news_id)
                    VALUES (?, ?)
                ''', (agent_id, news_id))
                conn.commit()
                logger.debug(f"Marked news_id {news_id} as processed by agent_id {agent_id}")
                return True
        except Exception as e:
            logger.error(f"Error marking news as processed: {str(e)}", exc_info=True)
            return False

    def has_agent_processed_news(self, agent_id: str, news_id: str) -> bool:
        """Check if a specific agent has processed a news item."""
        logger.debug(f"Checking if agent_id {agent_id} has processed news_id {news_id}")
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 1 FROM agent_news_processed
                    WHERE agent_id = ? AND news_id = ?
                    LIMIT 1
                ''', (agent_id, news_id))
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            logger.error(f"Error checking if agent processed news: {str(e)}", exc_info=True)
            return False

    def get_news_ids_processed_by_agent(self, agent_id: str) -> list:
        """Return a list of news_ids processed by the given agent_id."""
        logger.debug(f"Getting news_ids processed by agent_id: {agent_id}")
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT news_id FROM agent_news_processed WHERE agent_id = ?
                ''', (agent_id,))
                rows = cursor.fetchall()
                news_ids = [row[0] for row in rows]
                logger.debug(f"Found {len(news_ids)} news_ids processed by agent_id {agent_id}")
                return news_ids
        except Exception as e:
            logger.error(f"Error getting news_ids processed by agent: {str(e)}", exc_info=True)
            return [] 
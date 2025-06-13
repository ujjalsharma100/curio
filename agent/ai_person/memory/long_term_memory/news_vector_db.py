from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import os
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import logging

# Setup logging for news vector database
def setup_vector_db_logging():
    """Setup logging for the news vector database module."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, f"news_vector_db_{datetime.now().strftime('%Y%m%d')}.log")
    
    # Create logger
    logger = logging.getLogger("ai_person.memory.news_vector_db")
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
logger = setup_vector_db_logging()

class NewsVectorDB:
    def __init__(self, persist_directory: str = "news_vector_db"):
        """Initialize the news vector database.
        
        Args:
            persist_directory: Directory to persist the database
        """
        logger.info("Initializing NewsVectorDB")
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Create full path to database directory
        db_path = os.path.join(current_dir, persist_directory)
        logger.debug(f"Vector database path: {db_path}")
        
        # Initialize ChromaDB client with persistence
        logger.debug("Initializing ChromaDB client")
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Create embedding function using the model
        logger.debug("Creating embedding function with model: all-MiniLM-L6-v2")
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Get or create collection
        logger.debug("Getting or creating ChromaDB collection: ai_news")
        self.collection = self.client.get_or_create_collection(
            name="ai_news",
            embedding_function=self.embedding_function
        )
        logger.info("NewsVectorDB initialization complete")

    def add_news_item(self, news_item: Dict[str, Any]) -> str:
        """Add a news item to the vector database.
        
        Args:
            news_item: Dictionary containing news item data with keys:
                      title, summary, content, link, source, published
        
        Returns:
            str: The ID of the added news item
        
        """
        # Generate unique ID
        news_id = str(uuid.uuid4())
        logger.info(f"Adding news item to vector database: {news_item.get('title', 'No title')}")
        logger.debug(f"Generated news_id: {news_id}")
        
        try:
            # Add to collection
            logger.debug("Adding document to ChromaDB collection")
            self.collection.add(
                documents=[news_item["content"]],
                ids=[news_id]
            )
            logger.info(f"Successfully added news to vector database: {news_item['title']}")
            print(f"Successfully added news: {news_item['title']}")
            return news_id
        except Exception as e:
            logger.error(f"Error adding news item to vector database: {str(e)}", exc_info=True)
            print(f"Error adding news item: {str(e)}")
            raise

    def search_news(self, query: str, top_k: int = 3) -> List[str]:
        """Search for news items similar to the query.
        
        Args:
            query: Search query string
            top_k: Number of results to return
            
        Returns:
            List of news IDs that match the query
        """
        logger.info(f"Searching vector database with query: '{query}', top_k: {top_k}")
        try:
            logger.debug("Executing ChromaDB query")
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            # Return just the IDs
            news_ids = results['ids'][0]
            logger.info(f"Vector search completed, found {len(news_ids)} results")
            logger.debug(f"Found news IDs: {news_ids}")
            return news_ids
        except Exception as e:
            logger.error(f"Error searching news in vector database: {str(e)}", exc_info=True)
            print(f"Error searching news: {str(e)}")
            raise


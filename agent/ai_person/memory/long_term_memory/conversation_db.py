import sqlite3
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

# Setup logging for conversation database
def setup_conversation_db_logging():
    """Setup logging for the conversation database module."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, f"conversation_db_{datetime.now().strftime('%Y%m%d')}.log")
    
    # Create logger
    logger = logging.getLogger("ai_person.memory.conversation_db")
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
logger = setup_conversation_db_logging()

class ConversationDB:
    def __init__(self, db_path: str = "conversation.db"):
        """Initialize the conversation SQLite database.
        
        Args:
            db_path: Path to the SQLite database file
        """
        logger.info("Initializing ConversationDB")
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Create full path to database file
        self.db_path = os.path.join(current_dir, db_path)
        logger.debug(f"SQLite database path: {self.db_path}")
        self._create_tables()
        logger.info("ConversationDB initialization complete")
    
    def _create_tables(self):
        """Create necessary database tables if they don't exist"""
        logger.debug("Creating database tables if they don't exist")
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversations (
                        dialogue_id TEXT PRIMARY KEY,
                        agent_id TEXT NOT NULL,
                        dialogue TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                logger.debug("Database tables created/verified successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}", exc_info=True)
            raise
    
    def save_conversation(self, agent_id: str, dialogue_id: str, dialogue: str) -> bool:
        """Save a conversation dialogue to the SQLite database for a specific agent.
        
        Args:
            agent_id: Unique identifier for the agent
            dialogue_id: Unique identifier for the dialogue
            dialogue: The conversation dialogue text
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        logger.info(f"Saving conversation to SQLite database with agent_id: {agent_id}, dialogue_id: {dialogue_id}")
        logger.debug(f"Dialogue length: {len(dialogue)} characters")
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO conversations 
                    (dialogue_id, agent_id, dialogue)
                    VALUES (?, ?, ?)
                ''', (dialogue_id, agent_id, dialogue))
                conn.commit()
                logger.info(f"Successfully saved conversation to SQLite database: {dialogue_id} for agent {agent_id}")
                return True
        except Exception as e:
            logger.error(f"Error saving conversation to SQLite: {str(e)}", exc_info=True)
            print(f"Error saving conversation to SQLite: {str(e)}")
            return False
    
    def get_conversation(self, agent_id: str, dialogue_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a conversation for a specific agent from the database.
        
        Args:
            agent_id: ID of the agent
            dialogue_id: ID of the dialogue to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Conversation data if found, None otherwise
        """
        logger.debug(f"Retrieving conversation from SQLite database: agent_id={agent_id}, dialogue_id={dialogue_id}")
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT dialogue_id, agent_id, dialogue, created_at
                    FROM conversations
                    WHERE agent_id = ? AND dialogue_id = ?
                ''', (agent_id, dialogue_id))
                row = cursor.fetchone()
                
                if row:
                    conversation = {
                        'dialogue_id': row[0],
                        'agent_id': row[1],
                        'dialogue': row[2],
                        'created_at': row[3]
                    }
                    logger.debug(f"Successfully retrieved conversation: {dialogue_id} for agent {agent_id}")
                    return conversation
                else:
                    logger.warning(f"No conversation found with agent_id={agent_id}, dialogue_id={dialogue_id}")
                    return None
        except Exception as e:
            logger.error(f"Error retrieving conversation from SQLite: {str(e)}", exc_info=True)
            print(f"Error retrieving conversation: {str(e)}")
            return None
    
    def get_all_conversations(self, agent_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve all conversations for a specific agent from the database, ordered by creation time.
        
        Args:
            agent_id: ID of the agent
            limit: Optional limit on the number of conversations to return
            
        Returns:
            List[Dict[str, Any]]: List of conversation data
        """
        logger.debug(f"Retrieving all conversations from SQLite database for agent_id={agent_id}, limit: {limit}")
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if limit:
                    cursor.execute('''
                        SELECT dialogue_id, agent_id, dialogue, created_at
                        FROM conversations
                        WHERE agent_id = ?
                        ORDER BY created_at DESC
                        LIMIT ?
                    ''', (agent_id, limit))
                else:
                    cursor.execute('''
                        SELECT dialogue_id, agent_id, dialogue, created_at
                        FROM conversations
                        WHERE agent_id = ?
                        ORDER BY created_at DESC
                    ''', (agent_id,))
                
                rows = cursor.fetchall()
                conversations = []
                for row in rows:
                    conversation = {
                        'dialogue_id': row[0],
                        'agent_id': row[1],
                        'dialogue': row[2],
                        'created_at': row[3]
                    }
                    conversations.append(conversation)
                
                logger.debug(f"Successfully retrieved {len(conversations)} conversations for agent_id={agent_id}")
                return conversations
        except Exception as e:
            logger.error(f"Error retrieving conversations from SQLite: {str(e)}", exc_info=True)
            print(f"Error retrieving conversations: {str(e)}")
            return []
    
    def delete_conversation(self, agent_id: str, dialogue_id: str) -> bool:
        """Delete a conversation for a specific agent from the database.
        
        Args:
            agent_id: ID of the agent
            dialogue_id: ID of the dialogue to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        logger.info(f"Deleting conversation from SQLite database: agent_id={agent_id}, dialogue_id={dialogue_id}")
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM conversations
                    WHERE agent_id = ? AND dialogue_id = ?
                ''', (agent_id, dialogue_id))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Successfully deleted conversation: {dialogue_id} for agent {agent_id}")
                    return True
                else:
                    logger.warning(f"No conversation found to delete with agent_id={agent_id}, dialogue_id={dialogue_id}")
                    return False
        except Exception as e:
            logger.error(f"Error deleting conversation from SQLite: {str(e)}", exc_info=True)
            print(f"Error deleting conversation: {str(e)}")
            return False 
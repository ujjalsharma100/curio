from .long_term_memory import LongTermMemory
from .short_term_memory import ShortTermMemory
from typing import Dict, Any, Optional, List
from datetime import datetime

class Memory:

    def __init__(self):
        self.short_term_memory = ShortTermMemory()
        self.long_term_memory = LongTermMemory()
    

    def get_current_conversation(self, agent_id: str) -> str:
        return self.short_term_memory.get_current_conversation(agent_id)
    
    def get_current_conversation_prompt(self, agent_id: str) -> str:
        conversation_text = self.short_term_memory.get_current_conversation(agent_id)
        return f"""
        The following is the current converstation going on with timestamp, the person who said, and the dialouge.
        {conversation_text}
        """
    
    def add_dialogue_to_current_converstaion(self, agent_id: str, dialogue: str) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dialogue_with_timestamp = f"[{timestamp}] {dialogue}"
        self.short_term_memory.add_to_conversation_buffer(agent_id, dialogue_with_timestamp)
        self.long_term_memory.save_dialogue(agent_id, dialogue_with_timestamp)
        

    def save_news_item(self, agent_id: str, news_item: Dict[str, Any]) -> Optional[str]:
        return self.long_term_memory.save_news_item(agent_id, news_item)
    
    def get_news_item(self, agent_id: str, news_id: str) -> Optional[Dict[str, Any]]:
        return self.long_term_memory.get_news_item(agent_id, news_id)
    
    def search_relevant_news(self, agent_id: str, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        return self.long_term_memory.search_relevant_news(agent_id, query, top_k=top_k)
    
    def check_link_exists(self, agent_id: str, link: str) -> Optional[str]:
        """Check if a news link exists in long term memory. Returns news_id if found, else None."""
        return self.long_term_memory.check_link_exists(agent_id, link=link)
    
    def update_user_info(self, agent_id: str, field, value):
        return self.long_term_memory.update_user_information(agent_id, field=field, value=value)
    
    def get_information_about_the_human_prompt(self, agent_id: str) -> str:
        user_info_text = self.long_term_memory.get_user_information_text(agent_id)
        return f"""
        The following are the details that you know about the human based on past interactions. 
        {user_info_text}
        """

    def initialize_memory(self, agent_id: str) -> None:
        """Initialize memory for a new agent_id."""
        self.short_term_memory.initialize_short_term_memory(agent_id)
        self.long_term_memory.user_info.initialize_user_info(agent_id)

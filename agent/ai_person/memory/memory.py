from .long_term_memory import LongTermMemory
from .short_term_memory import ShortTermMemory
from typing import Dict, Any, Optional, List
from datetime import datetime

class Memory:

    def __init__(self):
        self.short_term_memory = ShortTermMemory()
        self.long_term_memory = LongTermMemory()
    

    def get_current_conversation(self) -> str:
        return self.short_term_memory.get_current_conversation()
    
    def get_current_conversation_prompt(self) -> str:
        conversation_text = self.short_term_memory.get_current_conversation()
        return f"""
        The following is the current converstation going on with timestamp, the person who said, and the dialouge.
        {conversation_text}
        """
    
    def add_dialogue_to_current_converstaion(self, dialogue: str) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dialogue_with_timestamp = f"[{timestamp}] {dialogue}"
        self.short_term_memory.add_to_conversation_buffer(dialogue_with_timestamp)
        self.long_term_memory.save_dialogue(dialogue_with_timestamp)
        

    def save_news_item(self, news_item: Dict[str, Any]) -> Optional[str]:
        return self.long_term_memory.save_news_item(news_item)
    
    def get_news_item(self, news_id: str) -> Optional[Dict[str, Any]]:
        return self.long_term_memory.get_news_item(news_id)
    
    def search_relevant_news(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        return self.long_term_memory.search_relevant_news(query, top_k=top_k)
    
    def check_link_exists(self, link: str) -> bool:
        return self.long_term_memory.check_link_exists(link=link)
    
    def update_user_info(self, field, value):
        return self.long_term_memory.update_user_information(field=field, value=value)
    
    def get_information_about_the_human_prompt(self) -> str:
        user_info_text = self.long_term_memory.get_user_information_text()
        return f"""
        The following are the details that you know about the human based on past interactions. 
        {user_info_text}
        """

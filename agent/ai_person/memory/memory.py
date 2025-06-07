from .long_term_memory import LongTermMemory
from .short_term_memory import ShortTermMemory

class Memory:

    def __init__(self):
        self.short_term_memory = ShortTermMemory()
        self.long_term_memory = LongTermMemory()
    

    def get_information_about_the_human_prompt(self) -> str:
        user_info_text = self.long_term_memory.get_user_information_text()
        return f"""
        The following are the details that you know about the human based on past interactions. 
        {user_info_text}
        """
    
    def update_user_info(self, field, value):
        return self.long_term_memory.update_user_information(field=field, value=value)

    def get_current_conversation(self) -> str:
        return self.short_term_memory.get_current_conversation()
    
    def get_current_conversation_prompt(self) -> str:
        conversation_text = self.short_term_memory.get_current_conversation()
        return f"""
        The following is the current converstation going on with timestamp, the person who said, and the dialouge.
        {conversation_text}
        """
    
    def add_dialogue_to_current_converstaion(self, dialogue: str) -> str:
        self.short_term_memory.add_to_conversation_buffer(dialogue)
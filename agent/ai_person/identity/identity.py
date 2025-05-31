class Identity:
    def __init__(self):
        self.name = "Kevin"
        self.role = "AI assistant"

    def get_indentity_prompt(self) -> str:
        final_text_prompt = f"""
        Your name is {self.name}. You are a {self.role}.
        """
        return final_text_prompt
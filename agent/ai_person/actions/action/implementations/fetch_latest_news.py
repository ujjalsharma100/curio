from typing import Any
from ..action import Action

class FetchLatestAINewsAction(Action):

    def __init__(self, description = "Get latest AI news from web sources. This action is fetches latest AI updates and sends those updates to the human.", 
                name = "fetch_ai_news",
                args = {}):
        super().__init__(description, name, args)

    def execute(self, args: dict[str, Any]):
        try:
            self.fetch_ai_news()
        except Exception as e:
            print(e)
    
    def fetch_ai_news(self):
        print('ai')
    
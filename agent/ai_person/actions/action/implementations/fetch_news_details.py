from typing import Any
from ..action import Action

class FetchNewsDetailsAction(Action):
    
    def __init__(self, description = "Get details and extra information regarding some update when the human wants it and send it to the human.", 
                name = "fetch_news_details",
                args = {}):
        super().__init__(description, name, args)

    def execute(self, args: dict[str, Any]):
        try:
            self.fetch_news_details()
        except Exception as e:
            print(e)
    
    def fetch_news_details(self):
        print('ai')
    
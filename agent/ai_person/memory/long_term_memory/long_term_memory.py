from .user_info import UserInfo

class LongTermMemory:

    def __init__(self):
        self.user_info = UserInfo()

    def get_user_information_text(self) -> str:
        return self.user_info.get_user_info_text()
    
    def update_user_information(self, field, value):
        return self.user_info.update_user_info(field=field, value=value)
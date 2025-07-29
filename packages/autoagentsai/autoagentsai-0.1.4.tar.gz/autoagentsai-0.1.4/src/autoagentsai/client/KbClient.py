from typing import Optional

class KbClient:
    def __init__(self, agent_id: str, auth_key: str, auth_secret: str, platform: str = "uat", jwt_token: Optional[str] = None):
        pass

    def create_kb(self, kb_name: str, kb_description: str, kb_type: str, kb_content: str):
        pass

    def get_kb(self, kb_id: str):
        pass
    
    
from pydantic import BaseModel

class ChattyContentText(BaseModel):
    body: str 
    preview_url: bool = False
    
    def get_body_or_caption(self) -> str:
        return self.body
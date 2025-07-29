from pydantic import BaseModel

class ChattyContentButton(BaseModel):
    text: str
    payload: str

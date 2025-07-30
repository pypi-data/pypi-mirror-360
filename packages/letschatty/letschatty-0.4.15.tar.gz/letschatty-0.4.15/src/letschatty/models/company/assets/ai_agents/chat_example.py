from pydantic import BaseModel, Field
from typing import List
from letschatty.models.messages import MessageDraft
from pydantic import field_validator


class ChatExample(BaseModel):
    """Example conversation for training the AI agent"""
    title: str = Field(..., description="Title/description of this example")
    messages: List[MessageDraft] = Field(..., description="Sequence of messages in this example")

    @field_validator('messages')
    @classmethod
    def validate_messages_not_empty(cls, v):
        if not v:
            raise ValueError("Chat example must contain at least one message")
        return v

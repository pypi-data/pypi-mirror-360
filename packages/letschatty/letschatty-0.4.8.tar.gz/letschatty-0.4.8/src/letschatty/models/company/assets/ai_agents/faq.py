from pydantic import BaseModel, Field
from typing import List

class FAQ(BaseModel):
    """FAQ item with question and answer"""
    question: str = Field(..., description="The question")
    answer: str = Field(..., description="The answer to the question")

from pydantic import BaseModel, Field


class ContextItem(BaseModel):
    """Individual context item with title and content"""
    title: str = Field(..., description="Title of the context section")
    content: str = Field(..., description="Content of the context section")
    order: int = Field(default=0, description="Order for displaying contexts")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "CABA Cases",
                "content": "If client is from CABA AND has irregularities AND wants to explore rights, schedule call",
                "order": 1
            }
        }


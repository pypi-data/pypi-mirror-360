
from .chat import Chat
from letschatty.models.company.assets import TagPreview, FlowPreview, ChattyAssetPreview, ContactPoint, Sale, ChattyAIAgentPreview

from letschatty.models.utils.types.serializer_type import SerializerType
from pydantic import BaseModel
from typing import List, Dict, Optional
import json

class ChatWithAssets(BaseModel):
    chat: Chat
    products: List[ChattyAssetPreview]
    tags: List[ChattyAssetPreview]
    sales: List[Sale]
    contact_points: List[ContactPoint]
    flows_links_states: List[FlowPreview]
    chatty_ai_agent: Optional[ChattyAssetPreview]

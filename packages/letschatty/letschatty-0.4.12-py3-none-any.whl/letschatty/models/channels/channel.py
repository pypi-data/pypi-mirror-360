from pydantic import BaseModel, SecretStr
from ..utils.types.channel_types import Channel
from enum import StrEnum
import os
from typing import Optional
META_GRAPH_URL = os.getenv("META_GRAPH_URL")

class ChannelInfo(BaseModel):
    channel_type: Channel

class MetaGraphPath(StrEnum):
    MESSAGES = "messages"
    MEDIA = "media"
    DATASET = "dataset"
    EVENTS = "events"
    PIXEL = "pixel"

class WhatsAppClientInfo(ChannelInfo):
    channel_type: Channel = Channel.WHATSAPP
    display_phone_number: str
    business_phone_number_id: str
    access_token: SecretStr
    waba_id: str
    dataset_id: Optional[str]

    @property
    def id(self) -> str:
        return f"{self.channel_type.value}_{self.business_phone_number_id}"

    def get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token.get_secret_value()}"
        }

    def get_media_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token.get_secret_value()}"
        }

    def get_url(self) -> str:
        return f"{META_GRAPH_URL}"

    def get_url_with_path(self, path:MetaGraphPath) -> str:
        match path:
            case MetaGraphPath.MESSAGES:
                return f"{META_GRAPH_URL}/{self.business_phone_number_id}/{path.value}"
            case MetaGraphPath.MEDIA:
                return f"{META_GRAPH_URL}/{self.business_phone_number_id}/{path.value}"
            case MetaGraphPath.DATASET:
                return f"{META_GRAPH_URL}/{self.waba_id}/{path.value}"
            case MetaGraphPath.EVENTS:
                if self.dataset_id is None:
                    raise ValueError("Dataset ID is not set for company, can't notify events to Meta Conversions API")
                return f"{META_GRAPH_URL}/{self.dataset_id}/{path.value}"
            case _:
                raise ValueError(f"Path {path} not found in MetaGraphPath")

from pydantic import BaseModel, Field
from .context_item import ContextItem
from typing import List, Optional
from letschatty.models.utils.types.identifier import StrObjectId

class FollowUpStrategy(BaseModel):
    """Individual context item with title and content"""
    maximum_consecutive_follow_ups: int = Field(default=3, description="Maximum number of consecutive follow ups to be executed")
    minimum_time_between_follow_ups: int = Field(default=1, description="Minimum time between follow ups in hours")
    follow_up_instructions_and_goals: str = Field(description="The detailed instructions for the follow up and the goals to be achieved")
    templates_allowed_rules: List[str] = Field(default_factory=list, description="In which situations the agent is allowed to send templates if the free conversation window is closed")
    follow_up_contexts: List[ContextItem] = Field(default_factory=list, description="Specific knowleadge base for the follow ups")
    only_on_weekdays: bool = Field(default=False, description="If true, the follow up will only be executed on weekdays")
    smart_follow_up_workflow_id: Optional[StrObjectId] = Field(default=None, description="The id of the smart follow up workflow to be assigned to the chat")

    @classmethod
    def example(cls) -> dict:
        return {
            "maximum_consecutive_follow_ups": 3,
            "minimum_time_between_follow_ups": 1,
            "follow_up_instructions_and_goals": "The detailed instructions for the follow up and the goals to be achieved",
            "templates_allowed_rules": ["The agent is allowed to send templates if the free conversation window is closed"],
            "follow_up_contexts": [{"title": "Context 1", "content": "Content 1"}, {"title": "Context 2", "content": "Content 2"}],
            "only_on_weekdays": False,
            "smart_follow_up_workflow_id": "000000000000000000000000",
        }
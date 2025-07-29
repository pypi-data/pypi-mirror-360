from enum import StrEnum

class ExecutorType(StrEnum):
    AGENT = "agent"
    WORKFLOW = "workflow"
    COPILOT = "copilot"
    SOURCE_AUTOMATION = "source_automation"
    TEMPLATE_AUTOMATION = "template_automation"
    MESSAGE_CAMPAIGN = "message_campaign"
    EXTERNAL_API = "external_api"
    SUGGESTION = "suggestion"
    SYSTEM = "system"
    OTHER = "other"
    META = "meta"
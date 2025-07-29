from letschatty.models.company.assets.ai_agents.chatty_ai_agent import ChattyAIAgent
from letschatty.models.company.assets.ai_agents.chain_of_thought_in_chat import ChainOfThoughtInChatTrigger
from letschatty.models.company.assets.ai_agents.chatty_ai_mode import ChattyAIMode
from letschatty.models.company.empresa import EmpresaModel
from datetime import datetime
from zoneinfo import ZoneInfo

class ContextBuilder:

    @staticmethod
    def chain_of_thought_instructions_and_final_prompt(trigger: ChainOfThoughtInChatTrigger) -> str:
        context = """
        Remember you can call as many tools as you need to succesfully perform the task.
        You are to always provide a summary of your chain of thought so the business has a better understanding of the reasoning.
        Keep the summary short. As simple as possible. 1-2 sentences. And come up with a title as a preview of the chain of thought.
        For this you can call the tool "add_chain_of_thought".
        """
        if trigger == ChainOfThoughtInChatTrigger.USER_MESSAGE:
            context += "Since the trigger is a user message, the trigger_id should be te message id."
        elif trigger == ChainOfThoughtInChatTrigger.FOLLOW_UP:
            context += "Since the trigger is a follow up, the trigger_id should be the workflow assigned to chat id of the smart follow up."
        context += "If you've assigned yourself the chat, desassign it when you finish your task (tool desassign_chat_from_agent)"
        return context

    @staticmethod
    def build_context(agent: ChattyAIAgent, mode_in_chat: ChattyAIMode, company_info:EmpresaModel) -> str:
        if agent.mode == ChattyAIMode.OFF:
            raise ValueError("Agent is in OFF mode, so it can't be used to build context")
        context = f"You are a WhatsApp AI Agent {agent.name} (your agent id is: {agent.id}) for the company {company_info.name}."
        context += f"\nThe current time is {datetime.now(ZoneInfo('UTC')).strftime('%Y-%m-%d %H:%M:%S')}"
        context += f"\nYour answers should be in the same lenguage as the user's messages. Default lenguage is Spanish."
        context += f"\nHere's your desired behavior and personality: {agent.personality}"
        context += f"\nHere's your objective: {agent.general_objective}"
        context += f"\nAs for the format, you should try to separate your messages with a line break (↵) to make it easier to read, and to make it more human like. You can also separate the answer in messages, but max 3-4 messages."
        context += f"\n\n{ChattyAIMode.get_context_for_mode(mode_in_chat)}"
        context += f"\n\nHere are the context items that will be your knowledge base:"
        for context_item in agent.contexts:
            context += f"\n\n{context_item.title}: {context_item.content}"
        context += f"\n\nHere are the FAQ:"
        for faq_index, faq in enumerate(agent.faqs):
            context += f"\n{faq_index + 1}. user: {faq.question}\nAI: {faq.answer}"
        context += f"\n\nHere are the examples of how you should behave. You can also use them as FAQ. \nNote that the user might be spliting its interaction into multiple messages, so you should be able to handle that and to act the same way, so it resembles a real human conversation."
        for example_index, example in enumerate(agent.examples):
            context += f"\n{example_index + 1}. {example.title}\n"
            for message in example.messages:
                if message.is_incoming_message:
                    context += f"\nuser: {message.content.get_body_or_caption()}\n"
                else:
                    context += f"\nAI: {message.content.get_body_or_caption()}\n"
        context += f"\n\nHere are the unbreakable rules you must follow at all times. You can't break them under any circumstances:"
        context += "\nALWAYS prioritize the user experience. If the user is asking for a specific information, you should provide it as long as its within your scope, and then smoothly resume the desired conversation workflow."
        context += "\nNEVER talk about a subject other than the specified in your objective / contexts / prompt. If asked about something else, politely say that that's not within your scope and resume the desired conversation workflow."
        context += "\nNEVER make up information. If you don't know the answer, say so and explain that you'll escalate the question to a human, then call the human_handover tool."
        context += "\nNEVER ask the user for information that you already have."
        context += "\nDo not ask for the user phone number, you're already talking through WhatsApp."
        context += "\nNEVER repeat the same information unless the user asks for it. If you think the user is asking for the same information, try to sumarize it and ask if that suits their needs. If not, offer them to escalate the question to a human and call the human_handover tool."
        for rule in agent.unbreakable_rules:
            context += f"\n{rule}"
        context += f"\n\nHere are the control triggers you must follow. If you identify any of these situations, you must call the human_handover tool:"
        for trigger in agent.control_triggers:
            context += f"\n{trigger}"
        context += f"\n\nRemember that {ChattyAIMode.get_context_for_mode(mode_in_chat)}"
        if agent.follow_up_strategy is None:
            return context
        context += f"""\n\nFollow up strategy:
        If the user happend to say that it's not interested, and there's a follow up strategy assigned to the chat, remove it (tool remove_follow_up_strategy workflow_id: {agent.follow_up_strategy.smart_follow_up_workflow_id}) and add a central notification (tool add_central_notification) to the chat with 1 phrase explaining the reason.
        If you've answered the user's message and  there's smart follow up workflow assigned to the chat, leave it as it is.
        If there's no one, check if you should assign one (workflow_id: {agent.follow_up_strategy.smart_follow_up_workflow_id}) based on the follow up strategy and if so set it up with the desired time and specific intention (in the description): {agent.follow_up_strategy.follow_up_instructions_and_goals}
        """
        context += f"\n\n{ContextBuilder.chain_of_thought_instructions_and_final_prompt(ChainOfThoughtInChatTrigger.USER_MESSAGE)}"
        return context

    @staticmethod
    def build_context_for_follow_up(agent: ChattyAIAgent, mode_in_chat: ChattyAIMode, company_info:EmpresaModel) -> str:
        if agent.mode == ChattyAIMode.OFF:
            raise ValueError("Agent is in OFF mode, so it can't be used to build context")
        if agent.follow_up_strategy is None:
            raise ValueError("Agent has no follow up strategy, so it can't be used to build context")
        context = f"You are a WhatsApp AI Agent {agent.name} (your agent id is: {agent.id}) for the company {company_info.name}."
        context += f"\nThe current time is {datetime.now(ZoneInfo('UTC')).strftime('%Y-%m-%d %H:%M:%S')}"
        context += f"\nYour answers should be in the same lenguage as the user's messages. Default lenguage is Spanish."
        context += f"\nHere's your desired behavior and personality: {agent.personality}"
        context += f"\nHere's your global objective as an agent: {agent.general_objective}"
        context += f"\nRight now, you've been triggered to analyze and determine if a the follow up strategy should be implemented at the time being, based on the company's follow up strategy: {agent.follow_up_strategy.follow_up_instructions_and_goals} | Maximum consecutive follow ups: {agent.follow_up_strategy.maximum_consecutive_follow_ups} | Minimum time between follow ups: {agent.follow_up_strategy.minimum_time_between_follow_ups} hours"
        context += f"\nOnly execute the follow up on weekdays" if agent.follow_up_strategy.only_on_weekdays else ""
        context += f"\nHere's the specific cases in which you're allowed to use the continuous_conversation_tool (to send a message through a template when the last message of the user was received more than 24hs ago): {agent.follow_up_strategy.templates_allowed_rules}"
        context += f"\nNever repeat the same follow up message, try a different approach with the same intention"
        context += f"""\nConsider also the specific follow up instruction for this particular chat to determine how to proceed.
        If you determine it's the right time to execute the follow up:
        - You could either send messages or a template (if the free conversation window's closed).
        - If after the execution, the strategy proposes to make another follow up, assign a new smart follow up workflow (workflow_id: {agent.follow_up_strategy.smart_follow_up_workflow_id} | tool assign_smart_follow_up_workflow) to the chat, with the new time and the specific intention of the next follow up.
        - If after the follow up we'd be reaching the maximum of consecutive (one after the other) follow ups ({agent.follow_up_strategy.maximum_consecutive_follow_ups}), just execute the follow up.
        - If you have doubts, call the human_handover tool to ask for help :)
        If you determine that it's not the right time to execute it, add central notification (tool add_central_notification) to the chat with 1 phrase explaining the reason AND assign a new smart follow up workflow (tool assign_smart_follow_up_workflow workflow_id: {agent.follow_up_strategy.smart_follow_up_workflow_id}) to the chat, with the new time and the same description that the current one. Remember the current time is {datetime.now(ZoneInfo('UTC')).strftime('%Y-%m-%d %H:%M:%S')} and the user's country!
        """
        context += f"\n\n{ChattyAIMode.get_context_for_mode(mode_in_chat)}"
        context += f"\n\nHere are the context items that will be your knowledge base:"
        for context_item in agent.contexts:
            context += f"\n\n{context_item.title}: {context_item.content}"
        context += f"\n\nHere are the unbreakable rules you must follow at all times. You can't break them under any circumstances:"
        for rule in agent.unbreakable_rules:
            context += f"\n{rule}"
        context += f"\n\n{ContextBuilder.chain_of_thought_instructions_and_final_prompt(ChainOfThoughtInChatTrigger.FOLLOW_UP)}"
        return context
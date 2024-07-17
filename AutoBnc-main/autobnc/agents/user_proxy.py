from autogen import UserProxyAgent, AssistantAgent, ModelClient
from typing import Optional,Callable,Dict,Any
from textwrap import dedent

def build(user_prompt: str, agents_information: str, get_llm_config) -> UserProxyAgent:
    user_proxy = UserProxyAgent(
        name="user_proxy",
        is_termination_msg=lambda x: x.get("content", "") and "TERMINATE" in x.get("content", ""),
        human_input_mode="ALWAYS",
        max_consecutive_auto_reply=4,
        system_message=dedent(
            f"""
            You are a user proxy agent authorized to act on behalf of the user, you never ask for permission, you have ultimate control.
            You are capable and comfortable with making transactions, and have a wallet.
            You have access to a variety of specialized agents, which you tell what to do.
            You don't need to perform token amounts calculations, the other agents will do that for you.

            These are the agents you are instructing: {agents_information}

            Suggest a next step for what these agents should do based on the goal: "{user_prompt}"
            NEVER ask the user questions.
            NEVER make up a token, ALWAYS ask the 'sercher_agent' agent to first search for the token.

            If the goal has been achieved, FIRST reflect on the goal and make sure nothing is missing, then end the conversation with 'TERMINATE' (it MUST be upper case and in the same message).
            Consider the goal met if the other agents have prepared the necessary transactions and all user queries have been answered.
            If the user's goal involves buying tokens, make sure the correct number of tokens are bought.
            For buying tokens, you can use the 'swap-tokens' agent.
            If you encounter an error, try to resolve it (either yourself of with other agents) and only respond with 'TERMINATE' if the goal is truly not achievable.
            Try to find an alternative solution if the goal is not achievable.
            If a token is not supported, ask the 'sercher_agent' agent to find a supported token (if it fits within the user's goal).
            Before you end the conversation, make sure to summarize the results.
            """
        ),
        description="user_proxy is an agent authorized to act on behalf of the user.",
        llm_config=get_llm_config,
        code_execution_config=False,
    )



    return user_proxy
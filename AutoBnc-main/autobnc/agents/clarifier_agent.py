import autogen.agentchat
from autogen import AssistantAgent,UserProxyAgent

from autobnc.util.constants import BINANCE_SECRET_KEY,BINANCE_API_KEY
from binance import Client
from typing import Annotated
from textwrap import dedent
from autobnc.util.agent_type import AgentInfo
name = "clarifier_agent"
description = "Clarifier is an assistant that can analyze a user's goal at the start of the conversation and determine if it is within the scope of the agents."
def build(user_proxy: UserProxyAgent,agents_information: str, interactive: bool,
          get_llm_config) -> AssistantAgent:
    missing_1 = dedent("""
            If the goal is not clear or missing information, you MUST ask for more information by calling the request_user_input tool.
            Always ensure you have all the information needed to define the goal that can be executed without prior context.
            Analyze the user's initial goal if there is missing information, and ask the user for it. 
            E.g. "Buy ETH" -> "How much ETH do you want to buy and with what token?"
            """ if interactive else "")

    missing_2 = dedent("""
            - Call the request_user_input tool if more information is needed to define the goal.
            """ if interactive else "")

    clarifier_agent = AssistantAgent(
        name = name,
        is_termination_msg=lambda x: x.get("content", "") and "TERMINATE" in x.get("content", ""),
        human_input_mode="ALWAYS",
        max_consecutive_auto_reply=4,
        system_message=dedent(
            f"""
                    Clarifier is an assistant that can analyze a user's goal at the start of the conversation and determine if it is within the scope of the agents.
                    The user will provide the goal, and the agents are meant to help prepare one or more necessary transactions to accomplish the goal.
                    When dealing with binance transactions, assume the following:
                        - When the user want to execute transactions he means to prepare the transactions.
                        - The agents can also research, discuss, plan actions and advise the user. All of that is in the scope of the agents.

                    You must analyze the goal to be executed by the agents.
                    If the goal is invalid or outside the scope of the agents, you MUST call the goal_outside_scope tool.
                    Only call goal_outside_scope if the goal is outside of the scope of what the agents can do.
                    If the goal is within the scope, you must call the `is_valid` function to check if the user's token is valid.

                    {
            missing_1
            }
                    DO NOT make any assumptions about the user's intent or context and ALWAYS take into account the available tools and their descriptions.

                    The available agents and tools:
                    {agents_information}
                    The agents can also: 
                    - Research 
                    - Discuss
                    - Plan actions and advise the user
                    - Develop purchase strategies
                    - Execute transactions
                    All of that is within scope of the agents.

                    The only things the clarifier should do are:
                    {
            missing_2
            }
                    - Call the goal_outside_scope tool if the goal is outside the scope of the agents.
                    - Nothing
                    Perform these actions ONLY in the BEGINNING of the conversation.
                    
                    
                    ### Example 1 ###
                    User: I need to analyze the market trends for ETHUSDT over the past 14 days. Can you fetch the k-line data and generate a candlestick chart for me?
                    Call is_valid with args:
                    {{
                        "symbol_or_asset": ETHUSDT,
                        "check_type"='symbol'
                    }}
                    """
        ),
        description=description,
        llm_config=get_llm_config,
        code_execution_config={"work_dir": "coding", "use_docker": False}

    )

    def is_valid(symbol_or_asset:str, check_type='symbol')->bool:
        api_key = BINANCE_API_KEY
        scret_key = BINANCE_SECRET_KEY
        client = Client(api_key, scret_key)
        # Get all symbols from exchange information
        exchange_info = client.get_exchange_info()
        if check_type == 'symbol':
            symbols = [s['symbol'] for s in exchange_info['symbols']]
            # Check if the provided symbol is in the list of valid symbols
            if symbol_or_asset in symbols:
                return True
            else:
                return False

        elif check_type == 'asset':
            base_assets = {s['baseAsset'] for s in exchange_info['symbols']}
            quote_assets = {s['quoteAsset'] for s in exchange_info['symbols']}
            assets = base_assets.union(quote_assets)
            # Check if the provided asset is in the list of valid assets
            if symbol_or_asset in assets:
                return True
            else:
                return False





    def goal_outside_scope(
            message: Annotated[
                str, "The message return to the user about why the goal is outside of the supported scope"],
    ) -> str:
        # notify_user(f"Goal not supported: {message}", "red")
        return "Goal not supported: TERMINATE"
    autogen.agentchat.register_function(
        goal_outside_scope,
        caller=clarifier_agent,
        executor=user_proxy,
        description="Notify the user about their goal not being in the scope of the agents"
    )
    autogen.agentchat.register_function(
        is_valid,
        caller=clarifier_agent,
        executor=user_proxy,
        description="Check if a given symbol or asset is valid on Binance. The function checks against either all trading symbols or all assets (base and quote) available on the Binance exchange, based on the provided check_type."
    )
    return clarifier_agent

def clarifier_info():
    clarifier_info = AgentInfo(name=name,tools=['goal_outside_scope','is_valid'],description=description)
    return clarifier_info
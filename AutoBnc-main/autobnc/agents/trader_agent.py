from autobnc.tool_build import FunctionBase

from autogen import AssistantAgent
from typing import Callable
from textwrap import dedent
from autobnc.intent import BuyIntent,SellIntent
from autobnc.util.agent_type import AgentInfo
from autobnc.AutoBnc import AutoBnc
name = "trader_agent"
description = dedent(
    f"""
    {name} is an AI assistant that's an expert at buying and selling tokens.
    """
)
system_message = dedent(f"""
    You are an expert at buying and selling tokens. Assist the user in their task of swapping tokens.
    ONLY focus on the buy and sell (swap) aspect of the user's goal and let other agents handle other tasks.
    You use the tools available to assist the user in their tasks.
    Below are examples, NOTE these are only examples and in practice you need to call the prepare_swap_token tool with the correct arguments.
    NEVER ask the user questions.
    Example 1:
            User: Buy 0.1 ETH 
            Call prepare_swap_token with args:
            {{
                "amount": 0.1,
                "symbol": "ETH"
                "direction": "buy"
            }}
    Example 2:
            User: Sell 1.2 BTC 
            Call prepare_swap_token with args:
            {{
                "amount": 1.2,
                "symbol": "BTC"
                "direction": "sell"
            }}

    Above are examples, NOTE these are only examples and in practice you need to call the prepare_swap_token tool with the correct arguments.
    """
                                       )

def build(get_llm_config) -> AssistantAgent:
    trader_agent = AssistantAgent(
        name = name,
        is_termination_msg=lambda x: x.get("content", "") and "TERMINATE" in x.get("content", ""),
        human_input_mode="NEVER",
        max_consecutive_auto_reply=4,
        system_message = system_message,
        description=description,
        llm_config=get_llm_config,
        code_execution_config={"work_dir": "coding", "use_docker": False}

    )

    return trader_agent

def transfer_info():
    trader_agent = AgentInfo(name=name,tools=['prepare_swap_token'],description=description)
    return trader_agent

class prepare_swap_token(FunctionBase):
    name: str = "prepare_swap_token"
    description: str = dedent(
            """
            Prepares a transfer transaction for buying and selling (swap) tokens
            """
        )
    def build(self, autobnc: 'AutoBnc') -> Callable[[float,str,str],str]:
        def run(
                amount: float,
                symbol:str,
                direction:str
            )->str:
                if direction == "buy":
                    intent = BuyIntent.create(
                        symbol=symbol,
                        amount=amount
                    )
                    autobnc.intents.append(intent)
                    return intent.summary
                elif direction =="sell":
                    intent = SellIntent.create(
                        symbol=symbol,
                        amount=amount
                    )
                    autobnc.intents.append(intent)
                    return intent.summary
                return "None"
        return run





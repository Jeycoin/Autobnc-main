import autogen.agentchat
from autogen import AssistantAgent,UserProxyAgent
from typing import Callable
from textwrap import dedent
from autobnc.intent import SendIntent
from autobnc.util.constants import BINANCE_SECRET_KEY,BINANCE_API_KEY
from binance import Client
from autobnc.util.agent_type import AgentInfo
from autobnc.AutoBnc import AutoBnc
from autobnc.tool_build import FunctionBase
name = "transfer_agent"
description = f"""
            {name} is an AI assistant that's an expert in handling transactions and balances on the Binance platform.
            The agent can fetch token balances and prepare transactions to send tokens.
            The agent can also prepare transfer transactions for given amounts in decimals for a token.
    """
def build(user_proxy: UserProxyAgent,
          get_llm_config) -> AssistantAgent:
    transfer_agent = AssistantAgent(
        name = name,
        is_termination_msg=lambda x: x.get("content", "") and "TERMINATE" in x.get("content", ""),
        human_input_mode="NEVER",
        max_consecutive_auto_reply=4,
        system_message = dedent(f"""
            You are an expert in Binance API and can assist the user in their tasks by fetching balances and preparing transactions to send tokens. 
            You are in a group of agents that will help the user achieve their goal. 
            ONLY focus on the sending and balance aspect of the user's goal and let other agents handle other tasks. 
            You use the tools available to assist the user in their tasks. 
            Your job is to only prepare the transactions by calling the prepare_transfer_transaction tool and the user will take care of executing them. 
            NOTE: There is no reason to call get_token_balance after calling prepare_transfer_transaction as the transfers are only prepared and not executed. 
            NOTE: A balance of a token is not required to perform a send, if there is an earlier prepared transaction that will provide the token. N
            EVER ask the user questions.

            Example 1:
            User: Send 0.1 ETH to vitalik.eth and then swap ETH to 5 USDC based on ETH network
            Call prepare_transfer_transaction with args:
            {{
                "amount": 0.1,
                "receiver": "sdajikojsdioauiofds",
                "symbol": "ETH"
                "network": "ETH"
            }}

            NOTE: the second transfer was not prepared because it's waiting for the swap transaction to be prepared first.

            Above are examples, NOTE these are only examples and in practice you need to call the tools with the correct arguments. NEVER respond with JSON.
            Take extra care in the order of transactions to prepare.
            IF a prepared swap transaction will provide the token needed for a transfer, you DO NOT need to call the get_token_balance tool.
    """
                                       ),
        description=description,
        llm_config=get_llm_config,
        code_execution_config={"work_dir": "coding", "use_docker": False}
    )



    def get_token_balance(token:str)->str:
        api_key = BINANCE_API_KEY
        scret_key = BINANCE_SECRET_KEY
        client = Client(api_key, scret_key)
        account_info = client.get_account()
        target_asset = 'USDT'
        for balance in account_info['balances']:
            if balance['asset'] == target_asset:
                free = balance['free']
                locked = balance['locked']
                return free
        return "0.00"

    autogen.agentchat.register_function(
        get_token_balance,
        caller=transfer_agent,
        executor=user_proxy,
        description="Check owner balance of token"
    )


    return transfer_agent


def transfer_info():
    transfer_info = AgentInfo(name=name,tools=['prepare_transfer_transaction','get_token_balance'],description=description)
    return transfer_info

class prepare_transfer_transaction(FunctionBase):
    name: str = "prepare_transfer_transaction"
    description: str = dedent(
            """
            Prepares a transfer transaction for given amount in decimals for a token
            """
        )
    def build(self, autobnc: 'AutoBnc') -> Callable[[float,str,str,str],str]:
        def run(
                amount: float,
                symbol:str,
                receiver:str,
                network:str,
            )->str:
                intent = SendIntent.create(
                        symbol=symbol,
                        amount=amount,
                        receiver=receiver,
                        network=network
                    )
                autobnc.intents.append(intent)
                return intent.summary
        return run
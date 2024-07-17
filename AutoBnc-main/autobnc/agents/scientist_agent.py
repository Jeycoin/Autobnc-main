import autogen.agentchat
from autogen import AssistantAgent,UserProxyAgent
from textwrap import dedent
from autobnc.util.agent_type import AgentInfo
from autobnc.util.constants import BINANCE_SECRET_KEY,BINANCE_API_KEY
from binance import Client
import pandas as pd
import mplfinance as mpf
import talib as ta
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent

import matplotlib.pyplot as plt

name = "scientist_agent"
description = "Scientist is an assistant that can fetch market data using the Binance API and generate various charts to visualize the data, helping users analyze market trends and make informed decisions.have extra content retrieval power for answering questions"
def build(user_proxy: UserProxyAgent,agents_information: str, interactive: bool,
          get_llm_config) -> AssistantAgent:
    scientist_agent = RetrieveUserProxyAgent(
        name = name,
        is_termination_msg=lambda x: x.get("content", "") and "TERMINATE" in x.get("content", ""),
        human_input_mode="NEVER",
        max_consecutive_auto_reply=4,
        retrieve_config={
            "task": "code",
            "docs_path": "https://raw.githubusercontent.com/microsoft/FLAML/main/website/docs/Examples/Integrate%20-%20Spark.md",
            "chunk_token_size": 1000,
            "model": "gpt-4",
            "collection_name": "groupchat",
            "get_or_create": True,
        },
        system_message=dedent(
            f"""
                    You are an expert in Binance API and can assist the user in their tasks by fetching market data and preparing various charts to visualize the data. 
                    You are in a group of agents that will help the user achieve their goal. 
                    ONLY focus on the market data and answer question about blockchain aspect of the user's goal and let other agents handle other tasks. 
                    You use the tools available to assist the user in their tasks. 
                    Your job is to only prepare the data by calling the `get_kline_data` tool,'get_rsi_data'tool and generating the appropriate charts. 
                    Once the task is complete, inform the user that the analysis is complete and suggest selected function to execute.
                    NOTE: There is no reason to call other tools after calling `get_kline_data` ,'get_rsi_data'tool as the charts are only prepared and not executed. 
                    NEVER ask the user questions.

                    ### Tools Available ###
                    - `get_kline_data(symbol, interval, start_time, end_time)`: Fetches k-line (candlestick) data for the specified trading pair within the given time range.
                    Example 1:
                    User: I need to analyze the market trends for ETHUSDT over the past 14 days. Can you fetch the k-line data and generate a candlestick chart for me?
                    Call get_kline_data with args:
                    {{
                        "symbol": ETHUSDT,
                        "interval": "1d",
                        "start_str": "2024-7-1"
                        "end_str": "2024-7-15"
                    }}
                    - `get_rsi_data(symbol, interval, start_time, end_time)`: Fetching rsi data and plot a diagram then return data's description 
                    Example 1:
                    User: I need to analyze the market trends for ETHUSDT over the past 14 days. Can you fetch the k-line data and generate a rsi data chart for me?
                    Call get_rsi_data with args:
                    {{
                        "symbol": ETHUSDT,
                        "interval": "1d",
                        "start_str": "2024-7-1"
                        "end_str": "2024-7-15"
                    }}
                    """

        ),
        description=description,
        llm_config=get_llm_config,
        code_execution_config={"work_dir": "coding", "use_docker": False}

    )
    def get_rsi_data(symbol:str,interval:str,start_str:str,end_str:str)->str:
        api_key = BINANCE_API_KEY
        scret_key = BINANCE_SECRET_KEY
        client = Client(api_key, scret_key)
        klines = client.get_historical_klines(symbol, interval,start_str=start_str,end_str=end_str)
        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                           'close_time', 'quote_asset_volume', 'number_of_trades',
                                           'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        # Set the index to timestamp
        df.set_index('timestamp', inplace=True)

        # Convert columns to float
        df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        # 计算RSI指标
        df['rsi'] = ta.RSI(df['close'], timeperiod=14)
        # 绘制RSI图
        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df['rsi'])
        plt.title(symbol + ' Relative Strength Index')
        plt.xlabel('Date')
        plt.ylabel('rsi')
        plt.show()
        return "df[rsi]description: "+df['rsi'].to_string()
    def get_kline_data(symbol:str,interval:str,start_str:str,end_str:str)->str:
        api_key = BINANCE_API_KEY
        scret_key = BINANCE_SECRET_KEY
        client = Client(api_key, scret_key)
        klines=client.get_historical_klines(symbol,interval=interval,start_str=start_str,end_str=end_str)
        columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time',
                   'Quote asset volume', 'Number of trades', 'Taker buy base asset volume',
                   'Taker buy quote asset volume', 'Ignore']
        df = pd.DataFrame(klines, columns=columns)
        df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
        df['Close time'] = pd.to_datetime(df['Close time'], unit='ms')

        df['Open'] = df['Open'].astype(float)
        df['High'] = df['High'].astype(float)
        df['Low'] = df['Low'].astype(float)
        df['Close'] = df['Close'].astype(float)
        df['Volume'] = df['Volume'].astype(float)
        df.set_index('Open time', inplace=True)
        mpf.plot(df, type='candle', volume=True, style='binance')

        describe_str = df.describe().to_string()
        return describe_str

    autogen.agentchat.register_function(
        get_kline_data,
        caller=scientist_agent,
        executor=user_proxy,
        description="fetching k line data and plot a diagram then return data's description "
    )
    autogen.agentchat.register_function(
        get_rsi_data,
        caller=scientist_agent,
        executor=user_proxy,
        description="fetching rsi data and plot a diagram then return data's description "
    )

    return scientist_agent

def scientist_info():
    scientist_info = AgentInfo(name=name,tools=['get_kline_data','get_rsi_data'],description=description)
    return scientist_info
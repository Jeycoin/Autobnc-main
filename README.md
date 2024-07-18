、
# 您好, 我是一枚金融助理! 👋
# AutoBnc-main

Autobnc-main 是一个 AI agent 项目，它可以帮助用户通过对话实现对虚拟货币市场的分析、虚拟货币的转账、购买、出售等功能，同时也可以介绍虚拟货币的相关知识。



## 功能特性
- **基于 AutoGen**：结合了多代理（multi-agents）、函数调用（function-call）、RAG 、groupchat的 AI 技术。
- **Binance-API**：通过 Binance-API 进行具体的 token 操作。
- **市场分析**：使用 TA-Lib 实现市场分析。
- **扩展性**：用户可以通过学习 agents 自主添加更多有处理能力的 agent。


## 🛠 技能
python-binance，autogen，ta-lib，openai等




## Agents

|      name     | function |
| ------------- | ------------- |
| user_proxy |用户代理，模拟用户沟通达成最终目标。|
| manager | 主持小组讨论，在每轮中选择speaker。直到讨论结果符合user_proxy要求结束小组对话|
| clarifier_agent | 检查用户输入是否符合当下语境，如不符合会要求用户重新给出prompt。|
| trader_agent | 创建虚拟货币的购买或者售出订单。|
| scientist_agent |有文档参考，同时可以通过binanceAPI访问市场数据并进行分析。 |
| transfer_agent | 创建虚拟货币的转账操作。|

## 使用方法/示例
配置OAI_CONFIG_LIST.json（示例）
```javascript
[
    {
        "model": "gpt-4",
        "api_key": "123",
        "tags": ["gpt-4", "tool"]
    },

    {
        "model": "gpt-3.5-turbo",
        "api_key": "123",
        "tags": ["gpt-3.5-turbo", "tool"]
    }
]
```
导入binanceAPI_KEY环境变量（需注意要开启相应权限并指定IP地址）：
```javascript
export BINANCE_API_KEY
export BINANCE_SECRET_KEY
```
最终执行命令：
```javascript
python pktest.py 
```

## 项目目录
```
│  agent_tool.py
│  AutoBnc.py
│  autobnc_type.py
│  intent.py
│  list.txt
│  setup_agents.py
│  tool_build.py
│  __init__.py
│  
├─agents
│      clarifier_agent.py
│      manager.py
│      scientist_agent.py
│      strategy_agent.py
│      trader_agent.py
│      transfer_agent.py
│      user_proxy.py
│      
└─util
        agent_type.py
        binanceSystem.py
        color.py
        constants.py
        __init__.py
```
## 文档
具体的项目文档可以参考：[文档](https://github.com/Jeycoin/Autobnc-main/blob/master/%E9%A1%B9%E7%9B%AE%E6%96%87%E6%A1%A3_20240718114640.pdf)

## 贡献
随时欢迎大家的贡献!

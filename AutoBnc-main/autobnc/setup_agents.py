from autobnc.agents import transfer_agent,user_proxy,clarifier_agent,scientist_agent,trader_agent

from autobnc.agent_tool import get_agents_information
from autobnc.AutoBnc import AutoBnc
import autogen
def set_up(autobnc:AutoBnc,agentInfoList:list,prompt,config)->list:
    agent_informations = get_agents_information(agentInfoList)
    user = user_proxy.build(prompt, agent_informations, config)
    transfer = transfer_agent.build(user, config)
    transfer_agent.prepare_transfer_transaction()
    clarifier = clarifier_agent.build(user, agent_informations, False, config)
    scientist = scientist_agent.build(user, agent_informations, False, config)
    trader = trader_agent.build(config)

    Func_prepare_transfer_transaction = transfer_agent.prepare_transfer_transaction()
    prepare_transfer_transaction_tool = transfer_agent.prepare_transfer_transaction.build(Func_prepare_transfer_transaction,autobnc)
    autogen.agentchat.register_function(
        prepare_transfer_transaction_tool,
        caller=transfer,
        executor=user,
        description=Func_prepare_transfer_transaction.description
    )

    Func_prepare_swap_token = trader_agent.prepare_swap_token()
    prepare_swap_token_tool = trader_agent.prepare_swap_token.build(Func_prepare_swap_token,autobnc)
    autogen.agentchat.register_function(
        prepare_swap_token_tool,
        caller=trader,
        executor=user,
        description=Func_prepare_swap_token.description
    )

    Agents = [user, transfer, clarifier, scientist, trader]

    return Agents
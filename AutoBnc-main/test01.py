from autobnc.agents import manager,transfer_agent,user_proxy,clarifier_agent,scientist_agent
from autobnc.agent_tool import get_agents_information
import autogen
from textwrap import dedent
from autobnc.util.constants import BINANCE_API_KEY
import os
if __name__ == '__main__':

    AgentInfoLIST = [transfer_agent.transfer_info(),clarifier_agent.clarifier_info(),scientist_agent.scientist_info()]
    information = get_agents_information(AgentInfoLIST)

    config_list = autogen.config_list_from_json(
        env_or_file="OAI_CONFIG_LIST.json",
        filter_dict={
            "model": ["gpt-4"],
        },
    )

    gpt3_config = {
        "cache_seed": 42,  # change the cache_seed for different trials
        "temperature": 0,
        "config_list": config_list,
        "timeout": 120,
    }
    print(type(gpt3_config))
    print("user begin:")
    prompt = input()
    print("Running AutoTx with the following prompt: " + prompt)
    user = user_proxy.build(prompt,information,gpt3_config)
    print("transfer begin:")
    transfer = transfer_agent.build(user,gpt3_config)
    print("clarifier_agent begin:")
    clarifier = clarifier_agent.build(user,information,False,gpt3_config)
    scientist = scientist_agent.build(user, information, False, gpt3_config)
    Agents = [user,transfer,clarifier,scientist]

    manager = manager.build(Agents,10,False,gpt3_config)

    chat = user.initiate_chat(
        manager,
        message=dedent(
            f"""
            I am currently connected with the Binance_API_Key: {BINANCE_API_KEY},
                        My goal is: {prompt} 
                        """
        )
    )
    print("char finished")

    if "ERROR:" in chat.summary:
        error_message = chat.summary.replace("ERROR: ", "").replace("\n", "")
        print(error_message, "red")
    else:
        print(chat.summary, "green")

    is_goal_supported = chat.chat_history[-1]["content"] != "Goal not supported: TERMINATE"

    os.system('pause')

from autobnc.util.agent_type import AgentInfo
def get_agents_information(infos:list[AgentInfo]):
    agent_descriptions = []
    for info in infos:
        description = f"Agent name: {info.name}\nDescription: {info.description}"
        agent_descriptions.append(description)
    informations = "\n".join(agent_descriptions)
    return informations

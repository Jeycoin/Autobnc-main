import click

from autobnc.agents import transfer_agent, clarifier_agent, scientist_agent,trader_agent
import autogen
from autobnc.util.constants import BINANCE_SECRET_KEY, BINANCE_API_KEY
from binance import Client
from autobnc.AutoBnc import AutoBnc
from autobnc.setup_agents import set_up
def autobnc_intro() -> None:
    print("""Welcome!
 $$$$$$\              $$\               $$$$$$$\                      
$$  __$$\             $$ |              $$  __$$\                     
$$ /  $$ |$$\   $$\ $$$$$$\    $$$$$$\  $$ |  $$ |$$$$$$$\   $$$$$$$\ 
$$$$$$$$ |$$ |  $$ |\_$$  _|  $$  __$$\ $$$$$$$\ |$$  __$$\ $$  _____|
$$  __$$ |$$ |  $$ |  $$ |    $$ /  $$ |$$  __$$\ $$ |  $$ |$$ /      
$$ |  $$ |$$ |  $$ |  $$ |$$\ $$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |      
$$ |  $$ |\$$$$$$  |  \$$$$  |\$$$$$$  |$$$$$$$  |$$ |  $$ |\$$$$$$$\ 
\__|  \__| \______/    \____/  \______/ \_______/ \__|  \__| \_______|                                                                                                                                                                                                        
    Source: 
    Support:2776778868@qq.com
    """)
@click.group()
def main() -> None:
    pass


@main.command()
@click.argument('prompt', required=False)
@click.option("-n", "--non-interactive", is_flag=True, help="Non-interactive mode (will not expect further user input or approval)")
def run_autobnc(prompt,non_interactive: bool):
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
    autobnc_intro()
    if prompt == None:
        prompt = click.prompt("What do you want to do?")
    api_key = BINANCE_API_KEY
    scret_key = BINANCE_SECRET_KEY
    client = Client(api_key, scret_key)
    AgentInfoLIST = [transfer_agent.transfer_info(), clarifier_agent.clarifier_info(), scientist_agent.scientist_info(),trader_agent.transfer_info()]
    atbnc = AutoBnc(client,gpt3_config)
    agents = set_up(atbnc,AgentInfoLIST,prompt,gpt3_config)
    atbnc.set_agents(agents)
    result = atbnc.run(prompt,non_interactive)
    if result.total_cost_without_cache > 0:
        print(f"LLM cost: ${result.total_cost_without_cache:.2f} (Actual: ${result.total_cost_with_cache:.2f})")

if __name__ == '__main__':
    run_autobnc()

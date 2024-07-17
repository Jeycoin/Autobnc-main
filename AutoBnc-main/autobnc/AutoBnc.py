import os
from datetime import datetime
import json
from typing import Optional
from autobnc.intent import Intent
from binance.client import Client
from autobnc.agents import manager
from textwrap import dedent
from termcolor import cprint
import asyncio
from autobnc.autobnc_type import RunResult,PastRun,EndReason
from autobnc.util.color import Color
from autobnc.util.constants import BINANCE_API_KEY
from autobnc.util.binanceSystem import run_intents
class AutoBnc:
    client: Client
    intents: list[Intent]
    agents: list
    config:dict
    agentInfoList:list
    current_run_cost_with_cache: float
    current_run_cost_without_cache:float
    info_messages:[]

    def __init__(self,client:Client,config:dict):
        self.client = client
        self.info_messages = []
        self.intents = []
        self.agents = []
        self.config = config
        self.current_run_cost_with_cache = 0
        self.current_run_cost_without_cache = 0
        self.user = None
    def run(self, prompt: str, non_interactive: bool, summary_method: str = "last_msg") -> RunResult:
        return asyncio.run(self.a_run(prompt, non_interactive, summary_method))

    async def a_run(self,prompt:str,non_interactive:bool,summary_method: str = "last_msg")->RunResult:
        total_cost_without_cache: float = 0
        total_cost_with_cache: float = 0
        info_messages = []
        while True:
            result = await self.try_run(prompt)
            total_cost_without_cache += result.total_cost_without_cache + self.current_run_cost_without_cache
            total_cost_with_cache += result.total_cost_with_cache + self.current_run_cost_with_cache
            info_messages += result.info_messages
            if result.end_reason == EndReason.TERMINATE or non_interactive:
                now = datetime.now()
                now_str = now.strftime('%Y-%m-%d-%H-%M-%S-') + str(now.microsecond)
                if not os.path.exists("costs"):
                    os.makedirs("costs")
                with open(f"costs/{now_str}.txt", "w") as f:
                    f.write(str(total_cost_without_cache))
                return RunResult(
                    result.summary,
                    result.chat_history_json,
                    result.intents,
                    result.end_reason,
                    total_cost_without_cache,
                    total_cost_with_cache,
                    info_messages
                )
            else:
                prompt_not_supported = "Prompt not supported. Please provide a new prompt."

                cprint(prompt_not_supported, "yellow")
                info_messages.append(prompt_not_supported)

                prompt = input("Enter a new prompt: ")
    async def try_run(self, prompt: str) -> RunResult:
        original_prompt = prompt
        past_runs: list[PastRun] = []
        while True:
            if past_runs:
                self.intents.clear()
            prev_history = "".join(
                [
                    dedent(f"""
                                    Then you prepared these transactions to accomplish the goal:
                                    {run.intents_info}
                                    Then the user provided feedback:
                                    {run.feedback}
                                    """)
                    for run in past_runs
                ]
            )
            prompt = (f"\nOriginaly the user said: {original_prompt}"
                      + prev_history
                      + "Pay close attention to the user's feedback and try again.\n")

            self.notify_user("Running AutoBnc with the following prompt: "+prompt,None)
            a_manager = manager.build(self.agents, 10, False, self.config)
            chat = self.user.initiate_chat(
                a_manager,
                message=dedent(
                    f"""
                        I am currently connected with the Binance_API_Key: {BINANCE_API_KEY},
                                    My goal is: {prompt} 
                                    """
                )
            )
            if "ERROR:" in chat.summary:
                error_message = chat.summary.replace("ERROR: ", "").replace("\n", "")
                self.notify_user(error_message, "red")
            else:
                self.notify_user(chat.summary, "green")
            is_goal_supported = chat.chat_history[-1]["content"] != "Goal not supported: TERMINATE"

            try:
                results = run_intents(self.client,self.intents)
                for result in results:
                    past_runs.append(PastRun(result[0], intents_info=result[1]))
                else:
                    break
            except Exception as e:
                self.notify_user(str(e), "red")
                break
        intents = self.intents.copy()
        self.intents.clear()
        chat_hitsory = json.dumps(chat.summary,indent=4)
        return RunResult(chat.summary,chat_hitsory,intents,EndReason.TERMINATE if is_goal_supported else EndReason.GOAL_NOT_SUPPORTED, float(chat.cost["usage_including_cached_inference"]["total_cost"]), float(chat.cost["usage_excluding_cached_inference"]["total_cost"]), self.info_messages)
    def notify_user(self, message: str, color: Optional[Color]) -> None:
        if color:
            cprint(message, color)
        else:
            print(message)
        self.info_messages.append(message)
    def set_agents(self,agents:list)->None:
        print("agent length:",len(agents))
        self.agents = agents
        self.user = agents[0]
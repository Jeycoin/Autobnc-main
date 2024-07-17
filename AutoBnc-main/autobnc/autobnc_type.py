from dataclasses import dataclass
from typing import Any, Dict, Optional, Callable, Union
from enum import Enum
from autobnc.intent import Intent
from binance.client import Client
@dataclass
class PastRun:
    feedback: str
    intents_info: str

class EndReason(Enum):
    TERMINATE = "TERMINATE"
    GOAL_NOT_SUPPORTED = "GOAL_NOT_SUPPORTED"

@dataclass
class RunResult:
    summary: str
    chat_history_json: str
    intents: list[Intent]
    end_reason: EndReason
    total_cost_without_cache: float
    total_cost_with_cache: float
    info_messages: list[str]




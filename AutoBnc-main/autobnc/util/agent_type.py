from dataclasses import dataclass, field
from typing import List

@dataclass
class AgentInfo:
    name:str
    tools: List[str]
    description: str



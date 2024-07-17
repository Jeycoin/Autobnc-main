from enum import Enum
from abc import abstractmethod
from typing import Union
from pydantic import BaseModel
from binance import Client
class IntentType(str, Enum):
    SEND = "send"
    BUY = "buy"
    SELL = "sell"

class IntentBase(BaseModel):
    type: IntentType
    summary: str




class SendIntent(IntentBase):
    receiver: str
    symbol: str
    amount: float
    network: str
    @classmethod
    def create(cls, symbol: str, amount: float, receiver: str, network: str) -> 'SendIntent':
        return cls(
            type=IntentType.SEND,
            symbol=symbol,
            amount=amount,
            receiver=receiver,
            network=network,
            summary=f"Transfer {amount} {symbol} to {receiver} on the {network} network"
        )
class BuyIntent(IntentBase):
    symbol: str
    amount: float
    @classmethod
    def create(cls, symbol:str, amount: float) -> 'BuyIntent':
        return cls(
            type=IntentType.BUY,
            symbol=symbol,
            amount=amount,
            summary=f"Buy {amount} {symbol}",
        )
class SellIntent(IntentBase):
    symbol: str
    amount: float
    @classmethod
    def create(cls, symbol:str, amount: float) -> 'SellIntent':
        return cls(
            type=IntentType.SELL,
            symbol=symbol,
            amount=amount,
            summary=f"Sell {amount} {symbol}",
        )



Intent = Union[SendIntent,BuyIntent,SellIntent]
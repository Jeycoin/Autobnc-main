from autobnc.intent import Intent,IntentType
from typing import List
from binance.client import Client
def run_intents(client:Client,intents:List[Intent]):
    results_with_info = []
    print("begin run intents:")
    for intent in intents:
        print(intent.summary,'\n')
        if intent.type == IntentType.BUY:
            order = client.order_market_buy(
                symbol=intent.symbol,
                quantity=intent.amount
            )
            results_with_info.append((order, intent.summary))
        if intent.type == IntentType.SELL:
            order = client.order_market_sell(
                symbol=intent.symbol,
                quantity=intent.amount
            )
            results_with_info.append((order, intent.summary))
        if intent.type == IntentType.SEND:
            order = client.withdraw(
                asset=intent.symbol,
                address=intent.receiver,
                amount=intent.amount,
                network=intent.network  # This parameter is optional
            )
            results_with_info.append((order, intent.summary))
    return results_with_info
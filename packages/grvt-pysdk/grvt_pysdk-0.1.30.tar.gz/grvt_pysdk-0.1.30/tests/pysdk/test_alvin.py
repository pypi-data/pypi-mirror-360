import time
import os
from decimal import Decimal

from pysdk.grvt_ccxt import GrvtCcxt
from pysdk.grvt_ccxt_env import GrvtEnv
from pysdk.grvt_ccxt_logging_selector import logger
from pysdk.grvt_ccxt_types import GrvtOrderSide


def send_mkt_order(
    api: GrvtCcxt, symbol: str, side: GrvtOrderSide, amount: Decimal, client_order_id: int
) -> dict:
    send_order_response: dict = api.create_order(
        symbol=symbol,
        order_type="market",
        side=side,
        amount=amount,
        params={"client_order_id": client_order_id},
    )
    logger.info(f"send mkt order: {send_order_response=} {client_order_id=}")
    return send_order_response


if __name__ == "__main__":
    parameter_dict = {
        "api_key": os.getenv("GRVT_API_KEY"),
        "trading_account_id": os.getenv("GRVT_TRADING_ACCOUNT_ID"),
        "private_key": os.getenv("GRVT_PRIVATE_KEY"),
    }
    api = GrvtCcxt(env=GrvtEnv.TESTNET, logger=None, parameters=parameter_dict)

    symbol = "BTC_USDT_Perp"  # CHANGE symbol
    side = "buy"
    amount = Decimal("0.01")
    client_order_id = int(time.time() * 1000)  # use timestamp in milliseconds for the client ord id

    send_mkt_order(api, symbol, side, amount, client_order_id)








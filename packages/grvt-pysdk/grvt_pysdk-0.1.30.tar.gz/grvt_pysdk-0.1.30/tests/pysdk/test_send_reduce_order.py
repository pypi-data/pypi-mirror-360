
import os

from pysdk.grvt_ccxt import GrvtCcxt
from pysdk.grvt_ccxt_env import GrvtEnv
from pysdk.grvt_ccxt_logging_selector import logger
from pysdk.grvt_ccxt_utils import rand_uint32

params = {
    "api_key": os.getenv("GRVT_API_KEY"),
    "trading_account_id": os.getenv("GRVT_TRADING_ACCOUNT_ID"),
    "private_key": os.getenv("GRVT_PRIVATE_KEY"),
}
env = GrvtEnv(os.getenv("GRVT_ENV", "testnet"))
test_api = GrvtCcxt(env, logger, parameters=params)
# create client order id
client_order_id = rand_uint32()
# _ = send_order(api, side="buy", client_order_id=client_order_id)
side: str = "buy"
price = 94_000
send_order_response = test_api.create_order(
    symbol="BTC_USDT_Perp",
    order_type="limit",
    side="buy",
    amount=0.01,
    price=94_000,
    params={
        "client_order_id": client_order_id,
        "reduce_only": True,
    },
)
logger.info(send_order_response)

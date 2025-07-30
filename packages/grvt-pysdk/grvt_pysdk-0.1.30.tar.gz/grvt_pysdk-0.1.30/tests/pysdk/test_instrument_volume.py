
import os

from pysdk.grvt_ccxt import GrvtCcxt
from pysdk.grvt_ccxt_env import GrvtEnv
from pysdk.grvt_ccxt_logging_selector import logger

params = {
    "api_key": os.getenv("GRVT_API_KEY"),
    "trading_account_id": os.getenv("GRVT_TRADING_ACCOUNT_ID"),
    "private_key": os.getenv("GRVT_PRIVATE_KEY"),
}
env = GrvtEnv(os.getenv("GRVT_ENV", "testnet"))
api = GrvtCcxt(env, logger, parameters=params)
# create client order id
markets = api.fetch_all_markets()
instruments: list[str] = [m["instrument"] for m in markets]
vols: list = []
for instrument in instruments:
    ticker: dict = api.fetch_ticker(instrument)
    buy_vol: float = float(ticker.get('buy_volume_24h_q', 0))
    sell_vol: float = float(ticker.get('sell_volume_24h_q', 0))
    vols.append((instrument, buy_vol + sell_vol))

vols.sort(key=lambda a: a[1], reverse=True)
for pair in vols:
    print(f"{pair[0]}: {pair[1]:.0f}")  # noqa: T201


import ccxt
import sys 

from pysdk.grvt_ccxt_logging_selector import logger

# from pysdk.grvt_ccxt_env import GrvtEnv
# from pysdk.grvt_ccxt_pro import GrvtCcxtPro

exchange = ccxt.paradex(
    {
        "enableRateLimit": True,
        "options": {
            "defaultType": "spot",
        },
    }
)
exchange.load_markets()
# print(f"Markets: {exchange.markets.values()}")
# book = exchange.fetch_order_book("ETH/USD:USDC")
# print(f"ETH book:\n{book}")
sys.exit(0)
exchange_desc = exchange.describe()
logger.info(f"Exchange Description: {list(exchange_desc)[0:20]}...")
required_features = ["margin", "fetchBalance", "fetchLeverageTiers"]
for feat in required_features:
    try:
        if not exchange.has[feat]:
            logger.warning(f"Exchange {exchange.name} | does not support: {feat}")
        else:
            logger.info(f"Exchange {exchange.name} | supports: {feat}")
    except KeyError:
        logger.warning(f"Exchange {exchange.name} | does not support: {feat}")
    except Exception as e:
        logger.warning(f"Exchange {exchange.name} | does not support: {feat} | {e}")

import os
from pysdk.grvt_raw_sync import GrvtRawSync
from pysdk.grvt_raw_base import GrvtApiConfig, GrvtError
from pysdk import grvt_raw_types
from pysdk.grvt_raw_env import GrvtEnv

# Set environment variables
# os.environ["GRVT_PRIVATE_KEY"] = "0xa00e077548ad302ff20a9ca9b74e32e278a91115b9a4d916fe39524733cd5525"
# os.environ["GRVT_API_KEY"] = "2y2VUnowiUuPJCY5EhzU6f8Puqs"
# os.environ["GRVT_TRADING_ACCOUNT_ID"] = "5318810780787313"
# os.environ["GRVT_ENV"] = "dev"
# os.environ["GRVT_END_POINT_VERSION"] = "v1"
# os.environ["GRVT_WS_STREAM_VERSION"] = "v1"

# Configure API
conf = GrvtApiConfig(
    env=GrvtEnv(os.getenv("GRVT_ENV", "testnet")),
    trading_account_id=os.getenv("GRVT_TRADING_ACCOUNT_ID"),
    private_key=os.getenv("GRVT_PRIVATE_KEY"),
    api_key=os.getenv("GRVT_API_KEY"),
    logger=None,
)

api = GrvtRawSync(config=conf)

# Prepare the request
req = grvt_raw_types.ApiFundingPaymentHistoryRequest(
    sub_account_id=str(api.config.trading_account_id),
    limit=2,  # Limit the number of records returned
    # Add more fields if required, e.g. instrument, start_time, end_time, limit, cursor
)

# Call the method
resp = api.funding_payment_history_v1(req)

# Handle the response
if isinstance(resp, GrvtError):
    print(f"Received error: {resp}")
elif resp.result is None:
    print("Expected funding payment history to be non-null")
else:
    print("Funding payment history result:")
    print(resp.result[0:2])  # Print first two items for brevity
    print(f"Total items: {len(resp.result)}")

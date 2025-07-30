import asyncio
from xts_api_client.xts_connect_async import XTSConnect
import os

API_key = os.getenv("INTERACTIVE_API_KEY")
API_secret = os.getenv("INTERACTIVE_API_SECRET")
API_source = os.getenv("API_SOURCE")
API_root = os.getenv("API_URL")


xt_interactive = XTSConnect(
apiKey = API_key,
secretKey = API_secret,
source = API_source,
root = API_root
)


async def main():
    await xt_interactive.interactive_login()
    
    respnse_get_dealer_orderbook = await xt_interactive.get_dealer_orderbook()
    list_of_order_in_dealer_orderbook = respnse_get_dealer_orderbook['result']
    print(f"Dealer Order Book: {list_of_order_in_dealer_orderbook}")
    
    await xt_interactive.interactive_logout()
if __name__ == "__main__":
    asyncio.run(main())

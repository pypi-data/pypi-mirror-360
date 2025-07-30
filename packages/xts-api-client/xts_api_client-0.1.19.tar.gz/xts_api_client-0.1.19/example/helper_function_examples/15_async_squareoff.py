import asyncio
from xts_api_client.xts_connect_async import XTSConnect
from xts_api_client.helper.helper import async_squareoff_all_positions_
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

    await async_squareoff_all_positions_(xt_interactive)
    
    await xt_interactive.interactive_logout()
if __name__ == "__main__":
    asyncio.run(main())
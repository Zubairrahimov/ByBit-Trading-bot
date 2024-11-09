from pybit.unified_trading import HTTP
import os
from dotenv import load_dotenv

load_dotenv()

session = HTTP(
    api_key=os.getenv('api'),
    api_secret=os.getenv("secret"),
    recv_window=60000

)

def get_balance():
    try:
        resp = session.get_wallet_balance(accountType="UNIFIED", coin="USDT")['result']['list'][0]['coin'][0]['walletBalance']
        resp = float(resp)
        return resp
    except Exception as err:
        print(err)

print(f'Your balance: {get_balance()} USDT')


class BybitClient:
    def __init__(self, api_key, api_secret):
        self.client = HTTP(
            api_key=api_key,
            api_secret=api_secret,
            recv_window=60000
        )


    def get_last_price(self, symbol):
        try:
            ticker = self.client.get_tickers(category="spot", symbol=symbol)
            print(ticker)  

            if 'result' in ticker and 'list' in ticker['result'] and len(ticker['result']['list']) > 0:
                last_price = float(ticker['result']['list'][0].get('lastPrice', 0))
                return last_price
            else:
                print("Error: Invalid or empty response structure.")
                return None
        except Exception as e:
            print(f"Error fetching last price: {e}")
            return None



    def place_order(self, symbol, side, qty):
        try:
            order_response = self.client.place_order(
                category="spot",
                symbol=symbol,
                side=side,
                orderType="Market",
                qty=qty
            )
            return order_response
        except Exception as e:
            print(f"Error placing order: {e}")
            return None


    def close_position(self, symbol, qty):
        try:
            
            rounded_qty = round(qty, 5) 
            order_response = self.client.place_order(
                category="spot",
                symbol=symbol,
                side="Sell",  
                orderType="Market",
                qty=rounded_qty
            )
            return order_response
        except Exception as e:
            print(f"Error closing position: {e}")
            return None



    def get_assets(self, coin):
        try:
            r = self.client.get_wallet_balance(accountType="UNIFIED")
            assets = {
                asset.get('coin'): float(asset.get('availableToWithdraw', '0.0'))
                for asset in r.get('result', {}).get('list', [])[0].get('coin', [])
            }
            return float(f"{assets.get(coin, 0.0):.8f}")
        except Exception as e:
            print(f"Error fetching assets: {e}")
            return 0.0



    def place_order(self, category, symbol, side, order_type, qty):
        try:
            return self.client.place_order(
                category=category,
                symbol=symbol,
                side=side,
                orderType=order_type,
                qty=qty
            )
        except Exception as e:
            print(f"Error placing order: {e}")
            return None


import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from bybit_client import get_balance , BybitClient
import asyncio
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
API_KEY = os.getenv("api")
API_SECRET = os.getenv("secret")


bybit_client = BybitClient(API_KEY, API_SECRET)


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        balance = get_balance()  
        if balance is not None:
            response = f"Your balance: {balance} USDT"
        else:
            response = "Could not retrieve your balance. Please try again later."
    except Exception as e:
        response = f"An error occurred: {e}"
    
    await update.message.reply_text(response)




async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome! You can trade using the following commands:\n"
        "/trade <amount_in_usdt> - Buy tokens\n"
        "/sell <amount_of_token> - Sell tokens\n"
        "/balance - Check your current usdt balance\n"
        "/autoclose - Automatic close your trade when it gets 0.1% profit\n"
    )

async def sell(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        amount = float(context.args[0]) if context.args else 0.0
        if amount <= 0:
            await update.message.reply_text("Please provide a valid amount in USDT.")
            return

        order_response = bybit_client.place_order(
            category="spot",
            symbol="BTCUSDT",
            side="SELL",
            order_type="Market",
            qty=amount
        )

        if order_response:
            await update.message.reply_text(f"Sell order placed successfully! Order Details: {order_response}")
            new_balance = bybit_client.get_assets("BTC")
            await update.message.reply_text(f"Your new BTC balance: {new_balance:.8f} BTC")
        else:
            await update.message.reply_text("Failed to place sell order.")

    except (IndexError, ValueError):
        await update.message.reply_text("Invalid input. Please use the command like: /sell <amount_in_usdt>")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")

trade_data = {}

async def autoclose_trade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global trade_data
    try:

        qty = bybit_client.get_assets("BTC")
        if qty < 0.00001:  # Minimum balance 
            await update.message.reply_text(
                "Insufficient BTC balance to start monitoring. You need at least 0.00001 BTC."
            )
            return

        # Getting the price of BTC/USDT
        initial_price = bybit_client.get_last_price("BTCUSDT")
        if initial_price is None:
            await update.message.reply_text("Failed to retrieve the initial BTCUSDT price. Monitoring cannot start.")
            return

        # Calculate the target close price (0.1% profit)
        target_close_price = initial_price * 1.001  # 0.1% profit
        trade_data['initial_price'] = initial_price
        trade_data['quantity'] = qty

        await update.message.reply_text(
            f"Monitoring BTCUSDT trade for 0.1% profit. Initial price set at {initial_price} USDT, "
            f"Quantity: {qty} BTC. The trade will close when the price reaches {target_close_price:.2f} USDT."
        )

        # Monitor the price and close the position when profit reaches 0.1%
        while True:
            await asyncio.sleep(10)

            current_price = bybit_client.get_last_price("BTCUSDT")
            if current_price is None:
                await update.message.reply_text("Error retrieving BTCUSDT price during monitoring.")
                continue

            percentage_change = ((current_price - initial_price) / initial_price) * 100

            if percentage_change >= 0.1:
                # Place the sell order to close the position
                order_response = bybit_client.close_position("BTCUSDT", qty)
                if order_response:
                    profit_usdt = (current_price - initial_price) * qty
                    await update.message.reply_text(
                        f"Your trade is auto-closed. Profit is 0.1% or higher.\n"
                        f"Profit in USDT: {profit_usdt:.2f} USDT\n"
                        f"Trade closed at {current_price:.2f} USDT."
                    )
                else:
                    await update.message.reply_text("Failed to close the BTCUSDT position.")
                break  

    except Exception as e:
        await update.message.reply_text(f"An error occurred during auto-closing: {e}")
        trade_data = {}  



async def trade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global trade_data  
    try:
        amount = float(context.args[0]) if context.args else 0.0
        if amount <= 0:
            await update.message.reply_text("Please provide a valid amount in USDT.")
            return

        order_response = bybit_client.place_order(
            category="spot",
            symbol="BTCUSDT",
            side="BUY",
            order_type="Market",
            qty=amount
        )

        if order_response:
            await update.message.reply_text(f"Buy order placed successfully! Order Details: {order_response}")
            new_balance = bybit_client.get_assets("BTC")
            await update.message.reply_text(f"Your new BTC balance: {new_balance} BTC")

            initial_price = bybit_client.get_last_price("BTCUSDT")
            if initial_price is not None:
                trade_data = {
                    'initial_price': initial_price,
                    'quantity': new_balance
                }
            else:
                await update.message.reply_text("Failed to retrieve initial price for trade data.")

        else:
            await update.message.reply_text("Failed to place buy order.")

    except (IndexError, ValueError):
        await update.message.reply_text("Invalid input. Please use the command like: /trade <amount_in_usdt>")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")



def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("trade", trade))
    application.add_handler(CommandHandler("sell", sell))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("autoclose", autoclose_trade))

    application.run_polling()



if __name__ == "__main__":
    main()

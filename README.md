# Bybit Trading Bot

A Python Telegram bot for trading on Bybit. It allows users to:
- Check account balance
- Place buy and sell orders
- Automatically close trades when reaching 0.1% profit

## Setup

1. Clone the repository:
   ```bash
   git clone  https://github.com/Zubairrahimov/ByBit_trading_telegram_bot.git
   cd yourrepository
   ```
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your environment variables in the `.env` file:
   ```env
   TELEGRAM_TOKEN=your_telegram_token
   API_KEY=your_bybit_api_key
   API_SECRET=your_bybit_api_secret
   ```

## Usage

- Run the bot:
  ```bash
  python bot.py
  ```


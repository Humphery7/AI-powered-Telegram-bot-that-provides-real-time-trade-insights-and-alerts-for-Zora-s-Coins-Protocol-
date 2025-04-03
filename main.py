import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, JobQueue
from textblob import TextBlob
from dotenv import load_dotenv
import os
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
import time
import asyncio

load_dotenv()

# Load your trained LSTM model
model = tf.keras.models.load_model('my_model.keras')

TOKEN = os.getenv('TOKEN')
COINGECKO_API_URL = 'https://api.coingecko.com/api/v3/coins/markets'
UNISWAP_API_URL = 'https://api.uniswap.org/v1/'
ZORA_BASE_API_URL = 'https://api.zora.co/transactions'
BLOCKSCOUT_URL = "https://eth.blockscout.com/api/v2/transactions"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Store user alert preferences
user_alerts = {}

# Store last seen transaction hash to avoid duplicates
last_seen_tx = None


async def get_trending_coins():
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",  # Sorting by market cap
        "per_page": 10,  # Fetching top 10 coins
        "page": 1,
        "sparkline": False
    }

    response = requests.get(COINGECKO_API_URL, params=params)
    if response.status_code != 200:
        return "Error fetching data from CoinGecko API."

    data = response.json()

    # Sorting by volume and price change percentage to determine trending coins
    trending_coins = sorted(
        data,
        key=lambda x: (x['market_cap'], x['total_volume'], x['price_change_percentage_24h']),
        reverse=True
    )[:5]  # Get top 5 coins

    return trending_coins


async def get_liquidity(token_address):
    response = requests.get(f"{UNISWAP_API_URL}liquidity/{token_address}")
    if response.status_code == 200:
        data = response.json()
        return data.get('liquidity', None)
    return None


async def get_zora_transactions():
    response = requests.get(ZORA_BASE_API_URL)
    if response.status_code == 200:
        return response.json()
    return []


def analyze_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_alerts:
        user_alerts[user_id] = False  # Default alerts off
    await update.message.reply_text("Hello! I'm your Zora Trading Insights bot. Type /help for commands.")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/trending - Get top 5 trending coins\n"
        "/recommend - AI suggests a coin to trade\n"
        "/alerts ON/OFF - Enable/disable notifications"
    )


async def trending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coins = await get_trending_coins()
    message = "Top 5 Trending Coins:\n"
    for i, coin in enumerate(coins, start=1):
        name = coin['name']
        symbol = coin['symbol'].upper()
        price = coin['current_price']
        change_24h = coin['price_change_percentage_24h']
        message += f"{i}️ ->  {name} ({symbol}) – ${price:,.2f} ({change_24h:+.2f}%)\n"
    await update.message.reply_text(message)


# CoinGecko API for real-time market data
def get_market_data(token_id):
    url = f'https://api.coingecko.com/api/v3/coins/{token_id}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching market data for {token_id}: {response.status_code}")
        return None


# BlockScout API for real-time transaction data
def get_transaction_data():
    response = requests.get(BLOCKSCOUT_URL)
    if response.status_code == 200:
        return response.json()['items']  # Assuming it returns a list of transactions
    else:
        print(f"Error fetching transaction data: {response.status_code}")
        return None


# CoinGecko Historical Price Data
def get_historical_data(token_id, vs_currency='usd', days=5):
    url = f'https://api.coingecko.com/api/v3/coins/{token_id}/market_chart'
    params = {'vs_currency': vs_currency, 'days': days}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return [price[1] for price in data['prices']]  # Extract only prices
    else:
        print(f"Error fetching historical data for {token_id}: {response.status_code}")
        return None


# Prepare the input data for the LSTM model (the same preprocessing you used during training)
def preprocess_data(historical_prices):
    scaler = MinMaxScaler()
    df = pd.DataFrame(historical_prices)
    df_scaled = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)

    sequence_length = 30  # Use the last 30 days for prediction
    X = []
    for i in range(len(df_scaled) - sequence_length):
        X.append(df_scaled.iloc[i:i + sequence_length].values)
    X = np.array(X)
    return X, scaler


# Get real-time transaction volume for the coin (using BlockScout API)
def get_transaction_volume(coin):
    transactions = get_transaction_data()
    if transactions:
        # Filter transactions involving the coin and calculate the total transaction volume
        volume = 0
        for tx in transactions:
            if tx['token_name'] == coin:  # Check if the coin is involved in the transaction
                volume += float(tx['value'])
        return volume
    return 0


# Get market data for recommendation
async def recommend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # List of coins to monitor
    coins_to_monitor = ['bitcoin', 'ethereum', 'binancecoin', 'cardano', 'ripple']

    # Get historical price data for all coins at once
    historical_data = {}
    for coin in coins_to_monitor:
        # Get historical price data for the last 30 days
        prices = get_historical_data(coin, days=30)
        if prices:
            historical_data[coin] = prices

    # Check if we have data for all coins
    if len(historical_data) != len(coins_to_monitor):
        await update.message.reply_text("Unable to get data for all coins. Try again later.")
        return

    # Create a DataFrame with historical prices for all coins
    df = pd.DataFrame(historical_data)

    # Make sure all coins have the same number of data points
    min_length = min(len(prices) for prices in historical_data.values())
    for coin in coins_to_monitor:
        historical_data[coin] = historical_data[coin][-min_length:]

    # Recreate DataFrame with aligned data
    df = pd.DataFrame(historical_data)

    # Scale the data
    scaler = MinMaxScaler()
    df_scaled = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)

    # Prepare the sequences for prediction
    sequence_length = 5
    X = []
    if len(df_scaled) >= sequence_length:
        # Take the last 30 days of data for prediction
        X = df_scaled.iloc[-sequence_length:].values.reshape(1, sequence_length, len(coins_to_monitor))
    else:
        await update.message.reply_text("Not enough historical data available.")
        return

    # Make prediction for all coins at once
    predicted_prices = model.predict(X)

    # Inverse transform to get actual prices
    predicted_prices = scaler.inverse_transform(predicted_prices.reshape(1, -1)).reshape(-1)

    # Store recommendations
    recommendations = []

    # Process each coin's prediction
    for i, coin in enumerate(coins_to_monitor):
        # Get real-time market data for the coin
        market_data = get_market_data(coin)
        if not market_data:
            continue

        current_price = market_data['market_data']['current_price']['usd']
        price_change_24h = market_data['market_data']['price_change_percentage_24h']
        market_cap = market_data['market_data']['market_cap']['usd']

        # Check if the coin is trending based on 24h price change, prediction
        recommendation = {
            'coin': coin,
            'current_price': current_price,
            'predicted_next_price': predicted_prices[i],
            'price_change_24h': price_change_24h,
            'market_cap': market_cap,
            'is_trending': price_change_24h > 5
        }

        # If the coin is trending or the predicted price is higher, recommend it
        if recommendation['is_trending'] or recommendation['predicted_next_price'] > current_price:
            recommendations.append(recommendation)

    # Prepare message to send back to user
    message = "Recommendations\n"
    for rec in recommendations:
        message += f"Coin: {rec['coin']}, Predicted Next Price: ${rec['predicted_next_price']:.2f}, Current Price: ${rec['current_price']:.2f}\n"

    if recommendations:
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("No recommendations at this time")


def fetch_transaction_data():
    try:
        # Fetch data from the Etherscan API
        response = requests.get(BLOCKSCOUT_URL)

        if response.status_code == 200:
            data = response.json()

            # Check if the transaction data contains items
            if 'items' in data:
                return data['items']
            else:
                print("No transaction data found.")
                return None
        else:
            print(f"Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None


async def alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if context.args:
        if context.args[0].lower() == 'on':
            user_alerts[user_id] = True
            await update.message.reply_text(
                "Real-time alerts enabled. You will now receive notifications for significant transactions.")
        elif context.args[0].lower() == 'off':
            user_alerts[user_id] = False
            await update.message.reply_text("Real-time alerts disabled. You will no longer receive notifications.")
        else:
            await update.message.reply_text("Invalid argument. Use /alerts ON or /alerts OFF.")
    else:
        # If no argument provided, show current status
        status = "ON" if user_alerts.get(user_id, False) else "OFF"
        await update.message.reply_text(f"Your alerts are currently {status}. Use /alerts ON or /alerts OFF to change.")


async def send_alert(context):
    global last_seen_tx
    transaction_data = fetch_transaction_data()

    if not transaction_data:
        return

    # Sort transactions by timestamp to get newest first
    transaction_data.sort(key=lambda x: x.get('timestamp', 0), reverse=True)

    # Check if we have a new transaction
    if transaction_data and transaction_data[0]['hash'] != last_seen_tx:
        latest_tx = transaction_data[0]
        last_seen_tx = latest_tx['hash']

        # Check if it's a significant transaction (value > 10 ETH)
        if float(latest_tx.get('value', 0)) > 10000000000000:  # 10 ETH in wei
            # Create alert message
            alert_message = (
                f"🚨 Significant Transaction Alert 🚨\n"
                f"Hash: {latest_tx['hash']}\n"
                f"From: {latest_tx['from']['hash'][:10]}...{latest_tx['from']['hash'][-6:]}\n"
                f"To: {latest_tx['to']['hash'][:10]}...{latest_tx['to']['hash'][-6:] if latest_tx['to'] else 'Contract Creation'}\n"
                f"Value: {float(latest_tx['value']) / 1e18:.4f} ETH\n"
                f"Gas: {latest_tx.get('gas_used', 'N/A')}\n"
                f"Status: {'✅ Success' if latest_tx.get('status') == '1' else '❌ Failed'}\n"
                f"Time: {latest_tx.get('timestamp', 'N/A')}"
            )

            # Send to all users who have alerts enabled
            for user_id, alerts_enabled in user_alerts.items():
                if alerts_enabled:
                    try:
                        await context.bot.send_message(chat_id=user_id, text=alert_message)
                    except Exception as e:
                        logger.error(f"Error sending alert to user {user_id}: {e}")


async def price_alert(context):
    """Check for significant price movements and send alerts"""
    # List of top coins to monitor
    coins_to_monitor = ['bitcoin', 'ethereum', 'binancecoin', 'cardano', 'ripple']

    for coin in coins_to_monitor:
        market_data = get_market_data(coin)
        if not market_data:
            continue

        price_change_24h = market_data['market_data']['price_change_percentage_24h']
        current_price = market_data['market_data']['current_price']['usd']

        # Alert if price change is significant (>5% in either direction)
        if abs(price_change_24h) > 5:
            direction = "📈 increased" if price_change_24h > 0 else "📉 decreased"
            alert_message = (
                f"📊 Price Alert for {market_data['name']} ({market_data['symbol'].upper()}) 📊\n"
                f"Price has {direction} by {abs(price_change_24h):.2f}% in the last 24 hours\n"
                f"Current price: ${current_price:,.2f}\n"
                f"Market cap: ${market_data['market_data']['market_cap']['usd']:,.0f}"
            )

            # Send to all users who have alerts enabled
            for user_id, alerts_enabled in user_alerts.items():
                if alerts_enabled:
                    try:
                        await context.bot.send_message(chat_id=user_id, text=alert_message)
                    except Exception as e:
                        logger.error(f"Error sending price alert to user {user_id}: {e}")


def main():
    # Create application instance
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("trending", trending))
    application.add_handler(CommandHandler("recommend", recommend))
    application.add_handler(CommandHandler("alerts", alerts))

    # Add job queue for periodic tasks
    job_queue = application.job_queue

    # Monitor transactions every 2 minutes
    job_queue.run_repeating(send_alert, interval=120, first=10)

    # Monitor price movements every 30 minutes
    job_queue.run_repeating(price_alert, interval=1800, first=5)

    # Start the bot
    application.run_polling()


if __name__ == '__main__':
    main()
# AI-Powered Telegram Bot for Zora Trading Insights

## Project Overview

The Zora Trading Insights bot is an AI-powered Telegram bot designed to provide real-time trade insights and alerts for users of Zora's Coins Protocol. By integrating data from Zora transactions, Base blockchain, CoinGecko, Uniswap, and using AI-powered trade insights, the bot helps users monitor cryptocurrency trends, track transaction activity, and receive intelligent trade suggestions based on market conditions.

## Core Features

### 1. **Real-Time Alerts**
- Monitor transactions on Zora's Coins Protocol (Base blockchain).
- Detect coins with significant surges or price changes.
- Notify users with real-time alerts when a coin gains momentum.

### 2. **AI-Powered Trade Insights**
- Use Natural Language Processing (NLP) to analyze comments and captions for sentiment analysis.
- Provide trade suggestions based on historical market data.
- Offer personalized recommendations for users to enhance trading decisions.

### 3. **Command-Based Interactions**
- `/trending` – Returns the top 5 trending coins by market cap and volume.
- `/recommend` – The AI provides a suggested coin to trade based on historical analysis.
- `/alerts ON/OFF` – Enables or disables real-time notifications.

### 4. **Integration with Zora’s Coins Protocol**
- Fetch transaction data from Zora’s API and Base blockchain logs.
- Display real-time trade volume, price changes, and other key metrics.
- Integration with Uniswap for direct trading links.

### 5. **Scalability & Optimization**
- Designed with lightweight architecture to ensure fast responses.
- Optimized for handling multiple transactions and real-time data processing.

## Tech Stack

- **Backend:** Python (Flask/FastAPI), Node.js (Express.js)
- **AI/NLP:** OpenAI API, TextBlob for sentiment analysis, TensorFlow (for LSTM model)
- **Data Sources:** Zora API, CoinGecko API, Uniswap API
- **Bot Frameworks:**
  - Telegram: python-telegram-bot library
  - Discord: discord.py (optional)
- **Hosting:** AWS Lambda, Heroku, or Vercel

## Installation

### Prerequisites
- Python 3.8+
- pip
- An active Telegram bot token (via BotFather)
- Environment variables stored in a `.env` file

### Steps to Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/zora-trading-bot.git
   cd zora-trading-bot
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables:**
   Create a `.env` file and add the following:
   ```env
   TOKEN=your_telegram_bot_token
   ```

4. **Run the Bot:**
   ```bash
   python bot.py
   ```

## How It Works

### **1. Real-Time Alerts**

The bot continuously monitors transactions from Zora’s Coins Protocol and the Base blockchain. When a new significant transaction (e.g., a large transfer) is detected, it sends an alert to users with active notifications.

### **2. AI-Powered Trade Recommendations**

The bot fetches historical price data for cryptocurrencies and processes it through an LSTM (Long Short-Term Memory) model for prediction. The model predicts the next price for the coins based on the last 30 days' data. When a coin shows potential for growth (based on prediction and current market behavior), the bot recommends it.

### **3. Trend Analysis & Sentiment Insights**

The bot uses TextBlob for sentiment analysis on comments and captions related to specific cryptocurrencies. This helps in analyzing the market mood, and the bot can provide insights on whether the sentiment around a coin is bullish or bearish.

### **4. Command Interaction**

- `/trending`: Fetches the top 5 trending cryptocurrencies by market cap, volume, and 24h price change.
- `/recommend`: Uses AI to suggest a cryptocurrency to trade based on predictive analytics.
- `/alerts ON/OFF`: Toggles real-time transaction alerts.

## Key Functions

### `get_trending_coins()`
Fetches the top 5 trending cryptocurrencies based on market capitalization and price change percentage from CoinGecko.

### `get_liquidity(token_address)`
Checks the liquidity of a specific token on Uniswap by querying the Uniswap API.

### `get_zora_transactions()`
Retrieves transaction data from Zora’s Coins Protocol to monitor activity.

### `analyze_sentiment(text)`
Analyzes text sentiment using TextBlob. Positive polarity indicates bullish sentiment, while negative polarity suggests bearish sentiment.

### `preprocess_data(historical_prices)`
Prepares historical price data for input to the LSTM model, using normalization and sequence formatting.

### `recommend(update, context)`
Provides an AI-powered recommendation based on LSTM predictions for the top coins.

### `send_alert(context)`
Sends alerts about significant transactions from the blockchain or price movements to users who have enabled notifications.

## Example Usage

- **/trending**: Get the list of the top 5 trending cryptocurrencies.
- **/recommend**: Receive a suggested coin to trade based on AI analysis.
- **/alerts ON**: Enable real-time alerts.
- **/alerts OFF**: Disable real-time alerts.

## Conclusion

The Zora Trading Insights bot is a powerful tool for cryptocurrency traders, providing real-time alerts, personalized trade recommendations, and market sentiment insights powered by AI. It is designed to be scalable and efficient, offering traders valuable information that helps them make data-driven decisions in real-time.

## Future Improvements

- **Expanded Coin Monitoring:** Add more coins to the monitoring list for broader recommendations.
- **Deep Learning Optimization:** Implement more advanced models like Transformers for improved price prediction accuracy.
- **User Personalization:** Allow users to customize their alerts and recommendations based on personal preferences.

---

For any questions or contributions, feel free to open an issue or pull request on the GitHub repository.


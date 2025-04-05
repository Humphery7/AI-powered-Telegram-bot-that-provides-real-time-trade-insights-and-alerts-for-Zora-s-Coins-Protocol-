# 🤖 Zora Trading Insights Bot

A Telegram bot that delivers real-time insights into activity on the **Zora protocol**, helping crypto users stay informed, make smarter decisions, and receive alerts on key on-chain movements — all within Telegram.

![Bot Preview](bot-video.gif)

## interact with bot at
[bot on telegram](t.me/zora_cryptobot)

---

## 🔧 Features

- **🧠 AI-Powered Recommendation (/recommend)**  
  An experimental feature that leverages machine learning to suggest a potentially interesting coin to trade. It considers historical transaction patterns, basic market trends, and other heuristics to make a smart guess.

- **📈 Trending Activity (/trending)**  
  Retrieves and summarizes trending tokens based on Zora-related metrics such as transaction frequency, volume, or user interactions. Ideal for spotting what's gaining traction on Zora.

- **🔔 Custom Alerts (/alerts ON | OFF)**  
  - `/alerts ON` enables background monitoring and sends you alerts when new transactions or notable activities occur on Zora.
  - `/alerts OFF` disables notifications so the bot will stay quiet unless directly interacted with.

- **💬 Sentiment Checker**  
  The bot can analyze any text message you input using basic NLP sentiment analysis. This helps gauge emotional tone, especially useful when you're reading tweets or messages about a token or project.

- **📚 Help Command (/help)**  
  Lists all the available commands and what they do, making it easy to get started.

---

## 🚀 Deployment

The bot is **live and continuously running on [PythonAnywhere](https://www.pythonanywhere.com/)** — no downtime, no stress. Just start chatting with it on Telegram.

---

## 💡 Available Commands

| Command        | Description                                                                 |
|----------------|-----------------------------------------------------------------------------|
| `/start`       | Initializes the bot and registers you for personalized alerts.              |
| `/help`        | Displays a list of all commands and how to use them.                        |
| `/trending`    | Shows currently active or popular Zora-related tokens based on on-chain activity. |
| `/recommend`   | Provides a coin recommendation using an AI model (in progress) and other metrics such as of coin.             |
| `/alerts ON`   | Turns on automatic alerts for Zora transaction activity.                    |
| `/alerts OFF`  | Turns off alerts so you stop receiving notifications.                       |

---

## 🛠️ Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/zora-trading-insights-bot.git
cd zora-trading-insights-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set environment variables

Create a `.env` file in the root folder and add your Telegram bot token:

```env
TOKEN=your_telegram_bot_token
```

### 4. Run the bot

```bash
python bot.py
```

---

## 🧠 Tech Stack

- **Python** (Asyncio)
- **python-telegram-bot**
- **TextBlob** (sentiment analysis)
- **TensorFlow** (for AI recommendations — work in progress)
- **Zora API** (core transaction data)

---

## deployment 

- **pythonAnywhere** 

## 📃 License

MIT License — free to use, modify, and contribute.


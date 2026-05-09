import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# .env file ကို load လုပ်ပါ (Render local run/dev ကိုင်ခိုင်း)
load_dotenv()

# .env ထဲမှာ သတ်မှတ်ထားတဲ့ Key ကိုသုံးပါ
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

if not GROQ_API_KEY or not TELEGRAM_BOT_TOKEN:
    raise Exception("GROQ_API_KEY or TELEGRAM_BOT_TOKEN is missing in environment variables!")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-70b-8192"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": user_message}]
    }
    try:
        resp = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=20)
        if resp.status_code == 200:
            output = resp.json()["choices"][0]["message"]["content"]
            await update.message.reply_text(output.strip())
        else:
            await update.message.reply_text(f"Groq API error: {resp.status_code}\n{resp.text}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot is running ...")
    app.run_polling()

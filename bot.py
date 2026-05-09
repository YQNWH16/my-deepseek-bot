import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from groq import Groq

# --- Web Server for Render ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Ai-16 is Online with Groq!')

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), SimpleHTTPRequestHandler).serve_forever(), daemon=True).start()

# --- Configs ---
API_ID = 35148850
API_HASH = '3426b7d98ab6a3599cd5b28925d1fcdd'
BOT_TOKEN = '8795982407:AAGs3_LFSa4qwWTEAC0i_m-T-qMPzWm-4JM'
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# --- Groq Setup ---
client = Groq(api_key=GROQ_API_KEY)
tg_client = TelegramClient('ai16_groq_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@tg_client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("Ai-16 is now powered by Groq (Free). How can I help you?")

@tg_client.on(events.NewMessage)
async def handle_chat(event):
    if not event.is_private or event.text.startswith('/'):
        return

    try:
        async with tg_client.action(event.chat_id, 'typing'):
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": event.text}],
                model="llama-3.3-70b-versatile",
            )
            response_text = chat_completion.choices[0].message.content
            await event.reply(response_text)
    except Exception as e:
        print(f"Error: {e}")
        await event.reply("I am having trouble connecting. Please try again.")

print("Bot is starting with Groq...")
tg_client.run_until_disconnected()

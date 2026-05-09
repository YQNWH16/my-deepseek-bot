import os
import threading
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from groq import Groq

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is Online')

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

API_ID = 35148850
API_HASH = '3426b7d98ab6a3599cd5b28925d1fcdd'
BOT_TOKEN = '8795982407:AAGs3_LFSa4qwWTEAC0i_m-T-qMPzWm-4JM'
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    sys.exit(1)

client = Groq(api_key=GROQ_API_KEY)
tg_client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@tg_client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("Ready.")

@tg_client.on(events.NewMessage)
async def handle(event):
    if not event.is_private or event.text.startswith('/'):
        return
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": event.text}],
            model="llama-3.3-70b-versatile",
        )
        await event.reply(chat_completion.choices[0].message.content)
    except Exception:
        pass

tg_client.run_until_disconnected()

import os
import threading
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from groq import Groq

# --- Web Server to satisfy Render's port check ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Ai-16 is running!')

def run_web_server():
    # Render uses 10000 by default, but we must use the environment PORT
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"Web server started on port {port}")
    server.serve_forever()

# Start the web server in a background thread immediately
threading.Thread(target=run_web_server, daemon=True).start()

# --- Configs ---
API_ID = 35148850
API_HASH = '3426b7d98ab6a3599cd5b28925d1fcdd'
BOT_TOKEN = '8795982407:AAGs3_LFSa4qwWTEAC0i_m-T-qMPzWm-4JM'
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("CRITICAL: GROQ_API_KEY is missing!")
    sys.exit(1)

# --- Clients Setup ---
client = Groq(api_key=GROQ_API_KEY)
tg_client = TelegramClient('ai16_session', API_ID, API_HASH)

@tg_client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("Ai-16 (Groq) is ready. How can I help you?")

@tg_client.on(events.NewMessage)
async def handle_message(event):
    if not event.is_private or event.text.startswith('/'):
        return
    try:
        async with tg_client.action(event.chat_id, 'typing'):
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": event.text}],
                model="llama-3.3-70b-versatile",
            )
            await event.reply(chat_completion.choices[0].message.content)
    except Exception as e:
        print(f"Chat Error: {e}")

# Start the Telegram Client
print("Telegram bot starting...")
tg_client.start(bot_token=BOT_TOKEN)
tg_client.run_until_disconnected()

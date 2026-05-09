import os
import threading
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from groq import Groq

# --- Simple Web Server to keep Render alive ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Ai-16 is running on Groq!')

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# --- Configurations ---
API_ID = 35148850
API_HASH = '3426b7d98ab6a3599cd5b28925d1fcdd'
BOT_TOKEN = '8795982407:AAGs3_LFSa4qwWTEAC0i_m-T-qMPzWm-4JM'
# Make sure this matches the key name in Render Environment
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("CRITICAL ERROR: GROQ_API_KEY not found in environment variables!")
    sys.exit(1)

# --- Initialize Clients ---
try:
    client = Groq(api_key=GROQ_API_KEY)
    tg_client = TelegramClient('ai16_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
except Exception as e:
    print(f"Startup Error: {e}")
    sys.exit(1)

@tg_client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("Ai-16 (Groq) is online and ready!")

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
            response = chat_completion.choices[0].message.content
            await event.reply(response)
    except Exception as e:
        print(f"Chat Error: {e}")
        await event.reply("Sorry, I'm experiencing a temporary connection issue.")

print("Bot deployed successfully. Listening for messages...")
tg_client.run_until_disconnected()

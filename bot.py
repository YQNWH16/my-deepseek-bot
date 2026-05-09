import os
import threading
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from groq import Groq

# --- Keep Render Alive ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Ai-16 Groq Bot is Active!')

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- Configurations ---
API_ID = 35148850
API_HASH = '3426b7d98ab6a3599cd5b28925d1fcdd'
BOT_TOKEN = '8795982407:AAGs3_LFSa4qwWTEAC0i_m-T-qMPzWm-4JM'
# Use the exact name from Render Environment
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("CRITICAL ERROR: GROQ_API_KEY not found in environment!")
    sys.exit(1)

# --- Clients Setup ---
client = Groq(api_key=GROQ_API_KEY)
tg_client = TelegramClient('ai16_groq_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@tg_client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("Ai-16 (Groq) is ready to help you!")

@tg_client.on(events.NewMessage)
async def handle_message(event):
    if not event.is_private or event.text.startswith('/'):
        return

    try:
        async with tg_client.action(event.chat_id, 'typing'):
            # Llama-3.3-70b is highly capable and free on Groq
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": event.text}],
                model="llama-3.3-70b-versatile",
            )
            response = chat_completion.choices[0].message.content
            await event.reply(response)
    except Exception as e:
        print(f"Error: {e}")
        await event.reply("Request limit reached or connection issue. Please wait 10 seconds.")

print("Bot is listening...")
tg_client.run_until_disconnected()

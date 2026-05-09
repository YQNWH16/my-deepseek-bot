import os
import threading
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from groq import Groq

# --- Step 1: Render Port Binding Fix ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Ai-16 is Online!')

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# --- Step 2: API Configurations ---
API_ID = 35148850
API_HASH = '3426b7d98ab6a3599cd5b28925d1fcdd'
BOT_TOKEN = '8625448440:AAExyh2aWcCZqlZ-PEyYe1o-sMLDkAjYy8o'
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("CRITICAL ERROR: GROQ_API_KEY not found in environment variables!")
    sys.exit(1)

# --- Step 3: Clients Initialization ---
client = Groq(api_key=GROQ_API_KEY)
tg_client = TelegramClient('ai16_session_v2', API_ID, API_HASH)

@tg_client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("Ai-16 is now online. I am ready to assist you!")

@tg_client.on(events.NewMessage)
async def handle_chat(event):
    if not event.is_private or event.text.startswith('/'):
        return

    try:
        async with tg_client.action(event.chat_id, 'typing'):
            # Using Llama 3.3 70B for fast and accurate responses
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": event.text}],
                model="llama-3.3-70b-versatile",
            )
            response_text = chat_completion.choices[0].message.content
            await event.reply(response_text)
    except Exception as e:
        print(f"Error: {e}")
        # Simple error handling for request limits
        await event.reply("System is currently busy. Please try again in 5 seconds.")

# --- Step 4: Run Bot ---
print("Bot deployment starting...")
tg_client.start(bot_token=BOT_TOKEN)
tg_client.run_until_disconnected()

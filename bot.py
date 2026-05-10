import os
import threading
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
import google.generativeai as genai

# --- Render Port Binding Fix ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Ai-16 Gemini Bot is Active!')

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# --- API Configurations ---
API_ID = 35148850
API_HASH = '3426b7d98ab6a3599cd5b28925d1fcdd'
BOT_TOKEN = '8625448440:AAExyh2aWcCZqlZ-PEyYe1o-sMLDkAjYy8o'
GEMINI_KEY = 'AIzaSyCQCXYFGdlzw_Ae0wNAKT0LLaRlXyr999c'

# --- Gemini Setup ---
genai.configure(api_key=GEMINI_KEY)
# High speed model to avoid timeouts
model = genai.GenerativeModel('gemini-1.5-flash')

# --- Telegram Client ---
tg_client = TelegramClient('ai16_gemini_new', API_ID, API_HASH)

@tg_client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("Hello! I am Ai-16. I am now powered by Gemini. How can I help you?")

@tg_client.on(events.NewMessage)
async def handle_message(event):
    if not event.is_private or event.text.startswith('/'):
        return

    try:
        async with tg_client.action(event.chat_id, 'typing'):
            # Send message to Gemini
            response = model.generate_content(event.text)
            if response and response.text:
                await event.reply(response.text)
    except Exception as e:
        print(f"Error: {e}")
        await event.reply("Service is temporarily busy. Please try again in a moment.")

# --- Start ---
print("Bot is starting with Gemini API...")
tg_client.start(bot_token=BOT_TOKEN)
tg_client.run_until_disconnected()

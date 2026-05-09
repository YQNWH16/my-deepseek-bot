import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
import google.generativeai as genai

# --- Render Web Server Configuration ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Ai-16 is Active and Online!')

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- API Configurations ---
API_ID = 35148850
API_HASH = '3426b7d98ab6a3599cd5b28925d1fcdd'
BOT_TOKEN = '8795982407:AAGs3_LFSa4qwWTEAC0i_m-T-qMPzWm-4JM'
GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY")

# --- Gemini AI Setup ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
chat_sessions = {}

# --- Telegram Client Setup ---
tg_client = TelegramClient('ai16_fix_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@tg_client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("Ai-16 is online. How can I help you today?")

@tg_client.on(events.NewMessage)
async def handle_chat(event):
    if not event.is_private or event.text.startswith('/'):
        return
    
    user_id = event.sender_id
    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[])

    try:
        async with tg_client.action(event.chat_id, 'typing'):
            response = chat_sessions[user_id].send_message(event.text)
            await event.reply(response.text)
    except Exception as e:
        print(f"Error: {e}")
        try:
            # Fallback in case of session error
            fallback_res = model.generate_content(event.text)
            await event.reply(fallback_res.text)
        except Exception as e2:
            print(f"Critical Error: {e2}")
            await event.reply("System is currently busy. Please try again in a moment.")

print("Bot is starting...")
tg_client.run_until_disconnected()

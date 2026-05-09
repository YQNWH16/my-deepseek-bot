import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
import google.generativeai as genai

# --- Render Web Server ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Gemini AI Bot is Online!')

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), SimpleHTTPRequestHandler).serve_forever(), daemon=True).start()

# --- Configs ---
API_ID = 35148850
API_HASH = '3426b7d98ab6a3599cd5b28925d1fcdd'
BOT_TOKEN = '8795982407:AAGs3_LFSa4qwWTEAC0i_m-T-qMPzWm-4JM'
GEMINI_API_KEY = 'AIzaSyA4loi7oX_d0csvWhPWcgqpmzS4N-dm_tk'

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
chat_sessions = {}

tg_client = TelegramClient('gemini_debug_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@tg_client.on(events.NewMessage)
async def handle_all(event):
    if not event.is_private or event.text.startswith('/'): return
    
    user_id = event.sender_id
    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[])

    async with tg_client.action(event.chat_id, 'typing'):
        try:
            # စာသား စကားပြောခြင်း
            response = chat_sessions[user_id].send_message(event.text)
            await event.reply(response.text)
        except Exception as e:
            # ဒီနေရာမှာ တက်တဲ့ Error ကို Render Logs ထဲမှာ မြင်ရအောင် လုပ်ထားပါတယ်
            print(f"!!! GEMINI ERROR: {e}")
            await event.reply(f"Error: {str(e)[:50]}... (Logs ကို စစ်ဆေးပေးပါ)")

print("Bot is starting with Debug Mode...")
tg_client.run_until_disconnected()

import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
import google.generativeai as genai

# --- Render Web Server (Port error မတက်စေရန်) ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Ai-16 is Active and Online!')

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), SimpleHTTPRequestHandler).serve_forever(), daemon=True).start()

# --- Configs ---
API_ID = 35148850
API_HASH = '3426b7d98ab6a3599cd5b28925d1fcdd'
BOT_TOKEN = '8795982407:AAGs3_LFSa4qwWTEAC0i_m-T-qMPzWm-4JM'
# Render Environment ထဲက Key ကို ဖတ်ခြင်း
GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)

# Model ကို နာမည်အတိုကောက်ဖြင့် ပြောင်းလဲသတ်မှတ်ခြင်း (404 Error ဖြေရှင်းရန်)
model = genai.GenerativeModel('gemini-1.5-flash')
chat_sessions = {}

tg_client = TelegramClient('ai16_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@tg_client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("Ai-16 အသင့်ရှိပါပြီ။ ဘာမေးချင်ပါသလဲ?")

@tg_client.on(events.NewMessage)
async def handle_chat(event):
    # Private chat မဟုတ်လျှင် သို့မဟုတ် Command ဖြစ်လျှင် ကျော်သွားမည်
    if not event.is_private or event.text.startswith('/'): return
    
    user_id = event.sender_id
    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[])

    try:
        # Typing status ပြပေးခြင်း
        async with tg_client.action(event.chat_id, 'typing'):
            response = chat_sessions[user_id].send_message(event.text)
            await event.reply(response.text)
    except Exception as e:
        print(f"Error: {e}")
        # Error တက်ခဲ့လျှင် Session အသစ်ပြန်စပြီး ထပ်စမ်းကြည့်ခြင်း
        try:
            new_chat = model.start_chat(history=[])
            res = new_chat.send_message(event.text)
            await event.reply(res.text)
            chat_sessions[user_id] = new_chat
        except:
            await event.reply("ခဏနေမှ ပြန်မေးကြည့်ပေးပါဦးခင်ဗျာ။")

print("Ai-16 is running successfully...")
tg_client.run_until_disconnected()

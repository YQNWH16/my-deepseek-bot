import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
import google.generativeai as genai

# --- Render Web Server (Render အမြဲနိုးနေစေရန်) ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Ai-16 is Running!')

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), SimpleHTTPRequestHandler).serve_forever(), daemon=True).start()

# --- Configs ---
API_ID = 35148850
API_HASH = '3426b7d98ab6a3599cd5b28925d1fcdd'
BOT_TOKEN = '8795982407:AAGs3_LFSa4qwWTEAC0i_m-T-qMPzWm-4JM'
# Render Environment ထဲက Key ကို ဖတ်ခြင်း
GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)

# --- 404 Error မတက်စေရန် Model အမည်ကို ပြင်ဆင်ခြင်း ---
# ရှေ့က 'models/' ကို ဖြုတ်လိုက်ပါသည်
model = genai.GenerativeModel('gemini-1.5-flash')
chat_sessions = {}

tg_client = TelegramClient('ai16_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@tg_client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("Ai-16 အသင့်ရှိပါပြီ။ ဘာမေးချင်ပါသလဲ?")

@tg_client.on(events.NewMessage)
async def handle_chat(event):
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
        # အမှားတက်ရင် တစ်ခါပြန်စမ်းကြည့်ဖို့ ကြိုးစားခြင်း
        try:
            res = model.generate_content(event.text)
            await event.reply(res.text)
        except:
            await event.reply("ခဏနေမှ ပြန်မေးကြည့်ပေးပါဦး။")

print("Bot is successfully starting...")
tg_client.run_until_disconnected()

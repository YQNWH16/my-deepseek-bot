import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
import google.generativeai as genai

# --- Web Server for Render ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Ai-16 Gemini is Online!')

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), SimpleHTTPRequestHandler).serve_forever(), daemon=True).start()

# --- Configurations ---
API_ID = 35148850
API_HASH = '3426b7d98ab6a3599cd5b28925d1fcdd'
BOT_TOKEN = '8795982407:AAGs3_LFSa4qwWTEAC0i_m-T-qMPzWm-4JM'

# Render Environment ထဲက Key ကို အလိုအလျောက် ဖတ်ယူခြင်း
GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction="သင်သည် Ai-16 ဖြစ်သည်။ မြန်မာဘာသာစကားဖြင့် သဘာဝကျကျနှင့် ယဉ်ကျေးစွာ ဖြေကြားပေးပါ။"
)
chat_sessions = {}

tg_client = TelegramClient('ai16_gemini_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@tg_client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("Ai-16 မှ ကြိုဆိုပါတယ်။ ဘာများ ကူညီပေးရမလဲခင်ဗျာ။")

@tg_client.on(events.NewMessage)
async def handle_chat(event):
    if not event.is_private or event.text.startswith('/'): return
    
    user_id = event.sender_id
    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[])

    async with tg_client.action(event.chat_id, 'typing'):
        try:
            response = chat_sessions[user_id].send_message(event.text)
            await event.reply(response.text)
        except Exception as e:
            print(f"Error: {e}")
            await event.reply("ခဏတာ အမှားရှိနေလို့ နောက်မှ ပြန်မေးကြည့်ပေးပါဦး။")

print("Ai-16 is running...")
tg_client.run_until_disconnected()

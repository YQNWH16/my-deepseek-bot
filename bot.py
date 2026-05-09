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
        self.wfile.write(b'Ai-16 is Online!')

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), SimpleHTTPRequestHandler).serve_forever(), daemon=True).start()

# --- Configs ---
API_ID = 35148850
API_HASH = '3426b7d98ab6a3599cd5b28925d1fcdd'
BOT_TOKEN = '8795982407:AAGs3_LFSa4qwWTEAC0i_m-T-qMPzWm-4JM'
GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)

# Model ကို အတိအကျ သတ်မှတ်ခြင်း
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
)

chat_sessions = {}

tg_client = TelegramClient('ai16_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@tg_client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("Ai-16 အဆင်သင့်ရှိပါပြီ။ ဘာကူညီပေးရမလဲ?")

@tg_client.on(events.NewMessage)
async def handle_chat(event):
    if not event.is_private or event.text.startswith('/'): return
    
    user_id = event.sender_id
    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[])

    try:
        response = chat_sessions[user_id].send_message(event.text)
        await event.reply(response.text)
    except Exception as e:
        print(f"Error: {e}")
        # Error တက်ရင် model အမည်ကို တစ်မျိုးပြောင်းစမ်းကြည့်ခြင်း
        await event.reply("ခဏလေးစောင့်ပေးပါ... စနစ်ကို ပြန်စစ်နေပါတယ်။")
        try:
            # တချို့ Region တွေမှာ model နာမည် အပြည့်အစုံ လိုတတ်လို့ပါ
            temp_model = genai.GenerativeModel('models/gemini-1.5-flash')
            temp_chat = temp_model.start_chat(history=[])
            response = temp_chat.send_message(event.text)
            await event.reply(response.text)
        except:
            await event.reply(f"Error: {str(e)[:50]}")

print("Bot is starting...")
tg_client.run_until_disconnected()

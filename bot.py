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

def run_server():
    httpd = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), SimpleHTTPRequestHandler)
    httpd.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- Configs ---
API_ID = 35148850
API_HASH = '3426b7d98ab6a3599cd5b28925d1fcdd'
BOT_TOKEN = '8795982407:AAGs3_LFSa4qwWTEAC0i_m-T-qMPzWm-4JM'
GEMINI_API_KEY = 'AIzaSyA4loi7oX_d0csvWhPWcgqpmzS4N-dm_tk'

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# User တစ်ဦးချင်းစီအတွက် Chat Session သိမ်းရန်
chat_sessions = {}

tg_client = TelegramClient('gemini_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@tg_client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("မင်္ဂလာပါ။ Gemini AI Bot အဆင်သင့်ရှိနေပါပြီ။ ဘာမေးချင်ပါသလဲ?")

@tg_client.on(events.NewMessage(pattern='/draw'))
async def draw(event):
    prompt = event.text.replace('/draw', '').strip()
    if not prompt: return await event.reply("ဆွဲချင်တဲ့ပုံကို စာသားနဲ့ ရေးပေးပါ။")
    await event.reply("ပုံဆွဲနေပါတယ်... 🎨")
    await event.reply(file=f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}")

@tg_client.on(events.NewMessage)
async def handle_all(event):
    if not event.is_private or event.text.startswith('/'): return
    
    user_id = event.sender_id
    # Session မရှိသေးရင် အသစ်ဖွင့်ပေးရန်
    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[])

    async with tg_client.action(event.chat_id, 'typing'):
        try:
            # ၁။ ဖိုင် သို့မဟုတ် ဓာတ်ပုံ ပါလာလျှင်
            if event.photo or event.voice or event.audio or event.document:
                path = await event.download_media()
                uploaded_file = genai.upload_file(path=path)
                # ဖိုင်နဲ့အတူ စာပါရင် ထည့်မေးပေးရန်
                user_msg = event.text if event.text else "ဒီပုံ သို့မဟုတ် ဖိုင်ကို ရှင်းပြပေးပါ။"
                response = model.generate_content([uploaded_file, user_msg])
                await event.reply(response.text)
                os.remove(path)
                return

            # ၂။ စာသားသက်သက် စကားပြောလျှင်
            if event.text:
                response = chat_sessions[user_id].send_message(event.text)
                await event.reply(response.text)

        except Exception as e:
            # Error အမှန်ကို သိနိုင်ဖို့ Log ထုတ်ထားခြင်း
            print(f"Error Details: {e}")
            # Session Error ဖြစ်ရင် အသစ်ပြန်ဖွင့်ပြီး စာပြန်ပို့ရန်
            chat_sessions[user_id] = model.start_chat(history=[])
            try:
                response = chat_sessions[user_id].send_message(event.text)
                await event.reply(response.text)
            except:
                await event.reply("ခေတ္တစောင့်ဆိုင်းပြီးမှ ပြန်မေးပေးပါ။")

print("Bot is successfully running...")
tg_client.run_until_disconnected()

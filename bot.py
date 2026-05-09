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
        self.wfile.write(b'Gemini AI Bot is Running!')

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), SimpleHTTPRequestHandler).serve_forever(), daemon=True).start()

# --- Configs ---
API_ID = 35148850
API_HASH = '3426b7d98ab6a3599cd5b28925d1fcdd'
BOT_TOKEN = '8795982407:AAGs3_LFSa4qwWTEAC0i_m-T-qMPzWm-4JM'
GEMINI_API_KEY = 'AIzaSyA4loi7oX_d0csvWhPWcgqpmzS4N-dm_tk'

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
# Chat history ကို မှတ်နိုင်ရန် model ကို session နဲ့ သုံးပါမည်
model = genai.GenerativeModel('gemini-1.5-flash')
chat_sessions = {}

tg_client = TelegramClient('gemini_only_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@tg_client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("မင်္ဂလာပါ။ ကျွန်တော်က Gemini AI ဖြစ်ပါတယ်။ အခု Groq မပါဘဲ Gemini တစ်ခုတည်းနဲ့ အလုပ်လုပ်နေပါပြီ။ ဘာကူညီရမလဲခင်ဗျာ။")

@tg_client.on(events.NewMessage(pattern='/draw'))
async def draw(event):
    prompt = event.text.replace('/draw', '').strip()
    if not prompt: return await event.reply("ဆွဲချင်တဲ့ပုံကို စာသားနဲ့ ရေးပေးပါ။")
    await event.reply("ပုံဆွဲနေပါတယ်... 🎨")
    # ပုံဆွဲရန်အတွက် Pollinations AI ကို ဆက်လက်သုံးစွဲပါမည်
    await event.reply(file=f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}")

@tg_client.on(events.NewMessage)
async def handle_all(event):
    if not event.is_private or event.text.startswith('/'): return
    
    user_id = event.sender_id
    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[])

    async with tg_client.action(event.chat_id, 'typing'):
        try:
            # ၁။ ဓာတ်ပုံ၊ အသံ သို့မဟုတ် ဖိုင်များ ဖြစ်လျှင်
            if event.photo or event.voice or event.audio or event.document:
                path = await event.download_media()
                uploaded_file = genai.upload_file(path=path)
                response = model.generate_content([uploaded_file, event.text or "ဒီဖိုင်အကြောင်း ရှင်းပြပေးပါ။"])
                await event.reply(response.text)
                os.remove(path)
                return

            # ၂။ စာသားသက်သက် စကားပြောလျှင် (Memory ပါဝင်သည်)
            if event.text:
                response = chat_sessions[user_id].send_message(event.text)
                await event.reply(response.text)

        except Exception as e:
            print(f"Error: {e}")
            await event.reply("ခဏတာ အမှားအယွင်းရှိနေပါတယ်။")

print("Gemini-Only Bot is Live!")
tg_client.run_until_disconnected()

import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from groq import Groq

# 1. Render မှာ Bot မအိပ်သွားအောင် Web Server အသေးစားလေး တစ်ခု တည်ဆောက်ခြင်း
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'AI Bot is Running!')

def run_web_server():
    # Render က ပေးတဲ့ Port ကို အသုံးပြုခြင်း
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"Web server started on port {port}")
    server.serve_forever()

# Web Server ကို Background မှာ သီးသန့် Run ထားခြင်း
threading.Thread(target=run_web_server, daemon=True).start()

# 2. --- Configurations (သင့်ရဲ့ အချက်အလက်များ) ---
API_ID = 35148850
API_HASH = '3426b7d98ab6a3599cd5b28925d1fcdd'
BOT_TOKEN = '8795982407:AAGs3_LFSa4qwWTEAC0i_m-T-qMPzWm-4JM'
GROQ_API_KEY = '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'

# 3. AI Client နှင့် Telegram Client ကို ချိတ်ဆက်ခြင်း
groq_client = Groq(api_key=GROQ_API_KEY)
tg_client = TelegramClient('ai_bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# /start command အတွက် အလုပ်လုပ်ပုံ
@tg_client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("မင်္ဂလာပါ။ ကျွန်တော်က Groq AI (Llama 3) Bot ဖြစ်ပါတယ်။ ဘာမေးချင်ပါသလဲခင်ဗျာ။")

# စာရိုက်လိုက်တိုင်း အဖြေပြန်ပေးမည့် အပိုင်း
@tg_client.on(events.NewMessage)
async def chat(event):
    # Private chat ဖြစ်ရမည်၊ စာသားပါရမည်၊ Command မဟုတ်ရပါ
    if event.is_private and event.text and not event.text.startswith('/'):
        async with tg_client.action(event.chat_id, 'typing'):
            try:
                # Groq AI ဆီက အဖြေတောင်းခြင်း
                completion = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant who speaks Myanmar and English fluently."},
                        {"role": "user", "content": event.text}
                    ],
                )
                
                # ရလာတဲ့ အဖြေကို Telegram သို့ ပြန်ပို့ခြင်း
                answer = completion.choices[0].message.content
                await event.reply(answer)
                
            except Exception as e:
                # Error တက်ခဲ့ရင် Logs မှာ ကြည့်နိုင်ရန်
                print(f"Error occurred: {e}")
                await event.reply("ခဏတာ အမှားအယွင်းရှိနေလို့ နောက်မှ ပြန်မေးပေးပါခင်ဗျာ။")

print("Bot is successfully starting...")
tg_client.run_until_disconnected()

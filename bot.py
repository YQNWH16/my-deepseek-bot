import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from openai import OpenAI

# Render မှာ Bot အမြဲနိုးနေစေဖို့ Web Server တစ်ခု ထည့်သွင်းထားခြင်း
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'DeepSeek AI Bot is Running!')

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# --- Configurations ---
API_ID = 35148850
API_HASH = '3426b7d98ab6a3599cd5b28925d1fcdd'
BOT_TOKEN = '8795982407:AAGs3_LFSa4qwWTEAC0i_m-T-qMPzWm-4JM'
DEEPSEEK_KEY = 'sk-387f3373b80e4470b397fa10997b807a' # သင့်ရဲ့ API Key ကို ထည့်ပေးထားပါတယ်

# AI Client နှင့် Telegram Client သတ်မှတ်ခြင်း
ai_client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com")
tg_client = TelegramClient('deepseek_bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@tg_client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("မင်္ဂလာပါ။ ကျွန်တော်က DeepSeek AI Bot ဖြစ်ပါတယ်။ ဘာမေးချင်ပါသလဲခင်ဗျာ။")

@tg_client.on(events.NewMessage)
async def chat(event):
    # Bot ကိုယ်တိုင်ပို့တဲ့စာတွေနဲ့ Command တွေကို ဖယ်ထုတ်ခြင်း
    if event.is_private and event.text and not event.text.startswith('/'):
        async with tg_client.action(event.chat_id, 'typing'):
            try:
                response = ai_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "You are a helpful and polite AI assistant who speaks Myanmar and English fluently."},
                        {"role": "user", "content": event.text},
                    ]
                )
                answer = response.choices[0].message.content
                await event.reply(answer)
            except Exception as e:
                print(f"Error: {e}")
                await event.reply("ခဏတာ အမှားအယွင်းရှိနေလို့ နောက်မှ ပြန်မေးပေးပါခင်ဗျာ။")

print("DeepSeek Bot is starting...")
tg_client.run_until_disconnected()

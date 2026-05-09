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
        self.wfile.write(b'Ai-16 Gemini is Online!')

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), SimpleHTTPRequestHandler).serve_forever(), daemon=True).start()

# --- Configs ---
API_ID = 35148850
API_HASH = '3426b7d98ab6a3599cd5b28925d1fcdd'
BOT_TOKEN = '8795982407:AAGs3_LFSa4qwWTEAC0i_m-T-qMPzWm-4JM'
GEMINI_API_KEY = 'AIzaSyA4loi7oX_d0csvWhPWcgqpmzS4N-dm_tk'

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
# မြန်မာစာ ဖြေဆိုမှု အားရစေရန် Instruction ထည့်ခြင်း
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction="သင်သည် Ai-16 အမည်ရှိသော အသိဉာဏ်မြင့် AI တစ်ဦးဖြစ်သည်။ မြန်မာဘာသာစကားကို အသုံးပြု၍ လူသားတစ်ယောက်ကဲ့သို့ သဘာဝကျကျ၊ ပြည့်စုံစွာနှင့် ယဉ်ကျေးစွာ ပြန်လည်ဖြေကြားပေးပါ။"
)
chat_sessions = {}

tg_client = TelegramClient('ai16_gemini_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@tg_client.on(events.NewMessage(pattern='/start'))
async def start(event):
    welcome_msg = (
        "Ai-16 မှ ကြိုဆိုပါတယ်။\n"
        "သင့်အနေနှင့် သိလိုသည်များကို မေးနိုင်ပြီး "
        "Ai-16 မှ မြန်ဆန်မှန်ကန်သော အဖြေများကိုပြောပြသွားပါမည်။"
    )
    await event.reply(welcome_msg)

@tg_client.on(events.NewMessage)
async def handle_chat(event):
    if not event.is_private or event.text.startswith('/'): return
    
    user_id = event.sender_id
    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[])

    async with tg_client.action(event.chat_id, 'typing'):
        try:
            # Gemini ထံမှ အဖြေတောင်းခြင်း
            response = chat_sessions[user_id].send_message(event.text)
            await event.reply(response.text)
        except Exception as e:
            print(f"Error: {e}")
            # Error ဖြစ်ပါက Session အသစ်ပြန်စရန်
            chat_sessions[user_id] = model.start_chat(history=[])
            await event.reply("တောင်းပန်ပါတယ်ခင်ဗျာ၊ ခဏတာ အမှားရှိနေလို့ နောက်တစ်ခါ ပြန်မေးကြည့်ပေးပါဦး။")

print("Ai-16 Gemini Bot is running...")
tg_client.run_until_disconnected()

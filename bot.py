import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
import google.generativeai as genai

# --- Render Web Server (Render ပေါ်မှာ Bot အမြဲပွင့်နေစေရန်) ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Ai-16 Gemini is Online and Ready!')

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), SimpleHTTPRequestHandler).serve_forever(), daemon=True).start()

# --- Configs ---
API_ID = 35148850
API_HASH = '3426b7d98ab6a3599cd5b28925d1fcdd'
BOT_TOKEN = '8795982407:AAGs3_LFSa4qwWTEAC0i_m-T-qMPzWm-4JM'

# Render ရဲ့ Environment Variable ထဲက Key ကို တိုက်ရိုက်ဆွဲယူခြင်း
GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not GEMINI_API_KEY:
    print("Warning: GOOGLE_API_KEY not found in Environment Variables!")

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction="သင်သည် Ai-16 ဖြစ်သည်။ မြန်မာဘာသာစကားဖြင့် အကျိုးရှိစွာ၊ သဘာဝကျကျနှင့် ယဉ်ကျေးပျူငှာစွာ ဖြေကြားပေးပါ။"
)
chat_sessions = {}

tg_client = TelegramClient('ai16_final_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

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
            # Gemini ကို စာပို့ခိုင်းခြင်း
            response = chat_sessions[user_id].send_message(event.text)
            await event.reply(response.text)
        except Exception as e:
            error_msg = str(e)
            print(f"Error Details: {error_msg}")
            
            # ဘာကြောင့် အမှားတက်သလဲဆိုတာ Bot က တိုက်ရိုက်ပြောပြပါလိမ့်မယ်
            if "API key not valid" in error_msg:
                await event.reply("Error: API Key မှားယွင်းနေပါတယ်။ Render မှာ ပြန်စစ်ပေးပါ။")
            elif "User location is not supported" in error_msg:
                await event.reply("Error: Region Block ဖြစ်နေပါတယ်။ Render Region ကို Singapore ပြောင်းပေးပါ။")
            else:
                await event.reply(f"ခဏတာ အမှားရှိနေပါတယ်ခင်ဗျာ။ (Error: {error_msg[:50]}...)")
            
            # Error တက်ရင် session အသစ်ပြန်စရန်
            chat_sessions[user_id] = model.start_chat(history=[])

print("Ai-16 Gemini is successfully starting...")
tg_client.run_until_disconnected()

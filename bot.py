import os
import threading
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from groq import Groq

# --- Render Port Binding Fix ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Ai-16 Bot is Running Successfully!')

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# --- Configuration ---
API_ID = 35148850
API_HASH = '3426b7d98ab6a3599cd5b28925d1fcdd'
BOT_TOKEN = '8795982407:AAGs3_LFSa4qwWTEAC0i_m-T-qMPzWm-4JM'
# Render Environment ထဲက GROQ_API_KEY ကို ဖတ်ခြင်း
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("Error: Please set GROQ_API_KEY in Render environment.")
    sys.exit(1)

# --- Clients Initialization ---
client = Groq(api_key=GROQ_API_KEY)
tg_client = TelegramClient('ai16_clean_session', API_ID, API_HASH)

@tg_client.on(events.NewMessage(pattern='/start'))
async def start(event):
    # ဒီနေရာမှာ ဘယ် link မှ မပါအောင် ဖယ်ထားပါတယ်
    await event.reply("Hello! I am Ai-16. How can I assist you today?")

@tg_client.on(events.NewMessage)
async def handle_message(event):
    if not event.is_private or event.text.startswith('/'):
        return

    try:
        async with tg_client.action(event.chat_id, 'typing'):
            # Llama-3.3-70b ကို သုံးထားလို့ အဖြေထွက် မြန်ပါလိမ့်မယ်
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": event.text}],
                model="llama-3.3-70b-versatile",
            )
            response = chat_completion.choices[0].message.content
            await event.reply(response)
    except Exception as e:
        print(f"Log Error: {e}")
        await event.reply("Service is temporarily busy. Please wait a moment.")

# --- Start Bot ---
print("Bot is starting clean...")
tg_client.start(bot_token=BOT_TOKEN)
tg_client.run_until_disconnected()

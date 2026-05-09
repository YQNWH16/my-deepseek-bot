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
        self.wfile.write(b'Ai-16 Bot is Online and Clean!')

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# --- Configs ---
API_ID = 35148850
API_HASH = '3426b7d98ab6a3599cd5b28925d1fcdd'
BOT_TOKEN = '8795982407:AAGs3_LFSa4qwWTEAC0i_m-T-qMPzWm-4JM'
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("CRITICAL: GROQ_API_KEY missing in Render environment!")
    sys.exit(1)

# --- AI Client with Strict Clean Instructions ---
# system_prompt ထဲမှာ ဘယ် channel link မှ မထည့်ဘဲ AI ကို အဖြေပဲပေးခိုင်းထားပါတယ်
client = Groq(api_key=GROQ_API_KEY)
SYSTEM_PROMPT = "You are Ai-16, a helpful assistant. Do not mention any Telegram channels or external links."

tg_client = TelegramClient('ai16_final_session', API_ID, API_HASH)

@tg_client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("Welcome! I am Ai-16. I am ready to help you without any advertisements.")

@tg_client.on(events.NewMessage)
async def handle_message(event):
    if not event.is_private or event.text.startswith('/'):
        return

    try:
        async with tg_client.action(event.chat_id, 'typing'):
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": event.text}
                ],
                model="llama-3.3-70b-versatile",
            )
            await event.reply(chat_completion.choices[0].message.content)
    except Exception as e:
        print(f"Error: {e}")
        await event.reply("I am a bit busy. Please try again in 5 seconds.")

print("Bot is starting up...")
tg_client.start(bot_token=BOT_TOKEN)
tg_client.run_until_disconnected()

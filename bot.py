import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from groq import Groq

# --- Web Server for Render ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Ai-16 Bot is Online!')

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), SimpleHTTPRequestHandler).serve_forever(), daemon=True).start()

# --- Configs ---
API_ID = 35148850
API_HASH = '3426b7d98ab6a3599cd5b28925d1fcdd'
BOT_TOKEN = '8795982407:AAGs3_LFSa4qwWTEAC0i_m-T-qMPzWm-4JM'
GROQ_API_KEY = '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'

client = Groq(api_key=GROQ_API_KEY)
tg_client = TelegramClient('ai16_stable_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Memory သိမ်းရန်
user_memory = {}

@tg_client.on(events.NewMessage(pattern='/start'))
async def start(event):
    # သင်အလိုရှိသော စာသားအတိအကျ
    welcome_msg = (
        "Ai-16 မှ ကြိုဆိုပါတယ်။\n"
        "သင့်အနေနှင့် သိလိုသည်များကို မေးနိုင်ပြီး "
        "Ai-16 မှ မြန်ဆန်မှန်ကန်သော အဖြေများကိုပြောပြသွားပါမည်။"
    )
    await event.reply(welcome_msg)

@tg_client.on(events.NewMessage(pattern='/draw'))
async def draw(event):
    prompt = event.text.replace('/draw', '').strip()
    if not prompt: return await event.reply("ဆွဲချင်တဲ့ပုံကို စာသားနဲ့ ရေးပေးပါ။")
    await event.reply("ပုံဆွဲနေပါတယ်... 🎨")
    image_url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"
    await event.reply(file=image_url)

@tg_client.on(events.NewMessage)
async def handle_chat(event):
    if not event.is_private or event.text.startswith('/'): return
    
    user_id = event.sender_id
    if user_id not in user_memory: user_memory[user_id] = []

    async with tg_client.action(event.chat_id, 'typing'):
        user_memory[user_id].append({"role": "user", "content": event.text})
        context = user_memory[user_id][-6:] 

        try:
            res = client.chat.completions.create(
                messages=[{"role": "system", "content": "You are Ai-16, a helpful Myanmar AI assistant."}] + context,
                model="llama-3.3-70b-versatile",
            )
            answer = res.choices[0].message.content
            user_memory[user_id].append({"role": "assistant", "content": answer})
            await event.reply(answer)
        except Exception as e:
            print(f"Error: {e}")
            await event.reply("ခဏတာ အမှားရှိနေပါတယ်။")

print("Ai-16 Bot is starting...")
tg_client.run_until_disconnected()

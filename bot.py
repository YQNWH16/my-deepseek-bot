import os
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events

# --- Web Server for Render/Keep Alive ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Ai-16 is Online with Gemini!')

threading.Thread(
    target=lambda: HTTPServer(
        ('0.0.0.0', int(os.environ.get("PORT", 10000))),
        SimpleHTTPRequestHandler
    ).serve_forever(),
    daemon=True
).start()

# --- Configs ---
API_ID = 35148850
API_HASH = '3426b7d98ab6a3599cd5b28925d1fcdd'
BOT_TOKEN = '8795982407:AAGs3_LFSa4qwWTEAC0i_m-T-qMPzWm-4JM'
GEMINI_API_KEY = "AIzaSyCQCXYFGdlzw_Ae0wNAKT0LLaRlXyr999c"  # သင့်ပေးသော Key

tg_client = TelegramClient('ai16_gemini_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

def ask_gemini(user_message, translate_to=None):
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

    if translate_to:
        prompt = f"Translate this to {translate_to}:\n{user_message}"
    else:
        prompt = user_message

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        resp = requests.post(api_url, json=payload, timeout=20)
        data = resp.json()
        return (
            data["candidates"][0]["content"]["parts"][0]["text"]
            if "candidates" in data
            else "Gemini API response error."
        )
    except Exception as e:
        print("Gemini API Error:", e)
        return "Gemini API Error, please try again later."

@tg_client.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.reply("Ai-16 is now powered by Gemini 💎!\nType any question or use /translate [lang] [text]")

@tg_client.on(events.NewMessage(pattern=r"/translate (\w+) (.+)"))
async def translate(event):
    m = event.pattern_match
    target_lang = m.group(1)
    text = m.group(2)
    async with tg_client.action(event.chat_id, 'typing'):
        reply = ask_gemini(text, translate_to=target_lang)
        await event.reply(reply)

@tg_client.on(events.NewMessage)
async def handle_chat(event):
    # Only reply in private, ignore commands
    if not event.is_private or event.text.startswith('/'):
        return
    async with tg_client.action(event.chat_id, 'typing'):
        reply = ask_gemini(event.text)
        await event.reply(reply)

print("Bot is starting with Gemini...")
tg_client.run_until_disconnected()

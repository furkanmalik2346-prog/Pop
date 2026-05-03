import asyncio
import os
import logging
import re
import random
from threading import Thread
from flask import Flask
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.constants import ChatType
from telegram.error import RetryAfter, TimedOut, NetworkError
from telegram.request import HTTPXRequest

# --- [ RENDER WEB SERVER TO KEEP ALIVE ] ---
app = Flask('')

@app.route('/')
def home():
    return "Rayuga Bot is running 24/7!"

def run_web():
    # Render automatic 'PORT' environment variable provide karta hai
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- [ LOGGING ] ---
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.WARNING
)

# --- [ CONFIGURATION ] ---
OWNER_ID = 8708136512
BOT_TOKENS = [
    "7976898164:AAF0EOd7zDcR-2AsYAFmV5jaGXN653m7DFM",
    "8241343991:AAHLz-N7pyiUFEn7Pby1M-onsKRel2EHwLQ",
    "8630973207:AAFThDx9rnDVTc2Q2wz9B6r4WeDwrm8B0i0",
    "8676299399:AAGuSTreaZf7HluYvgAtbvYKHhxB6xhUwDA",
    "8649501393:AAGflUj6bRYMUBCmB3c3x4CSPszzSIUK9n0",
    "8740017909:AAHfAldL_AlhKZjnHeLfw_JrZq8QEqUtyaQ",
    "8666232041:AAFcGb41-1mYq2e1iSE9r9oTYaGBwys-kFM"
]

# --- [ MESSAGES SECTION ] ---
HEART_EMOJIS = ['❤️', '🧡', '💛', '💚', '💙', '💜', '🤎', '🖤', '🤍', '💘', '💝', '💖', '💗', '💓', '💞', '💌', '💕', '💟', '♥️', '❣️', '💔']
TIME_NC_MESSAGES = [
    " {target} Tɪᴍᴇ Is Oᴠᴇʀ 12:382:229",
    " {target} Tᴇʀɪ Mᴀᴀ Kᴀ Bʜᴏsᴅᴀ Sɪʟ Dᴜɴ 12:382:230",
    " {target} Tᴇʀᴀ Bᴀᴀᴘ Rᴀʏᴜɢᴀ 12:382:231",
    " {target} Tɪᴍᴇ Tᴏ Dɪᴇ Mᴄ 12:382:233",
]
REPLY_MESSAGES = [
    "{target} Tᴇʀɪ ᴍᴀᴀ ɢᴜʟᴀᴍ ʜ ʙᴇᴛᴇ🐣",
    "{target} ʙᴏʟᴇ Rᴀʏᴜɢᴀ Kɪ ᴊᴀɪ Hᴏ🕳️🔥",
    "{target} ᴛᴇʀɪ ᴍᴀᴀ ʙᴏʟᴇ Rᴀʏᴜɢᴀ अब्बू ʜᴀɪ ᴍᴇʀᴇ🩴🔥",
]
SPAM_MESSAGE_TEMPLATE = "{target} ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝑲𝑬𝑵𝑰𝑵-𝑹𝑨𝒀𝑼𝑮𝑨 𝑲𝑨 कुतिया के 🥂🌙"

# --- [ BOT ENGINE ] ---
class BotInstance:
    def __init__(self, bot_number, owner_id):
        self.bot_number = bot_number
        self.owner_id = owner_id
        self.active_tasks = {}

    async def start(self, update, context):
        if update.effective_user.id != self.owner_id: return
        help_text = "🚀 **𝐑𝐀𝐘𝐔𝐆𝐀 𝐕2 𝐄𝐍𝐆𝐈𝐍𝐄** 🚀\n\n-attack <text>\n-spam <text>\n-stopall"
        await update.message.reply_text(help_text, parse_mode='Markdown')

    # Note: Baaki NC/Spam loops aapki original file wale logic par based hain
    async def attack_logic(self, update, context):
        if update.effective_user.id != self.owner_id: return
        # Attack Logic Implementation here...

async def run_bot(token, bot_number, owner_id):
    request = HTTPXRequest(connection_pool_size=100, read_timeout=15, write_timeout=15)
    application = Application.builder().token(token).request(request).build()
    
    bot_logic = BotInstance(bot_number, owner_id)
    application.add_handler(CommandHandler("start", bot_logic.start))
    
    # Error handling to prevent crash
    try:
        await application.initialize()
        await application.start()
        await application.updater.start_polling(drop_pending_updates=True)
        print(f"✅ Rayuga Bot {bot_number} Active")
        await asyncio.Event().wait()
    except Exception as e:
        print(f"❌ Bot {bot_number} crashed: {e}")

async def main():
    # Web server ko background mein start karna
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

    print(f"Rayuga System Starting for {OWNER_ID}...")
    tasks = [run_bot(token, i+1, OWNER_ID) for i, token in enumerate(BOT_TOKENS)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

import asyncio
import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.constants import ChatType
from telegram.error import RetryAfter, TimedOut, NetworkError
import logging
import re
import random
from telegram.request import HTTPXRequest
from flask import Flask
from threading import Thread

# --- [ RENDER WEB SERVER ] ---
app = Flask('')

@app.route('/')
def home():
    return "Rayuga Bot is running 24/7!"

def run_web():
    # Render automatic 'PORT' environment variable provide karta hai
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- [ LOGGING ] ---
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.WARNING
)

# --- [ CONFIGURATION ] ---
# Aapki nayi Owner ID
OWNER_ID = 8708136512

# Aapke naye 7 tokens
BOT_TOKENS = [
    "7976898164:AAF0EOd7zDcR-2AsYAFmV5jaGXN653m7DFM",
    "8241343991:AAHLz-N7pyiUFEn7Pby1M-onsKRel2EHwLQ",
    "8630973207:AAFThDx9rnDVTc2Q2wz9B6r4WeDwrm8B0i0",
    "8676299399:AAGuSTreaZf7HluYvgAtbvYKHhxB6xhUwDA",
    "8649501393:AAGflUj6bRYMUBCmB3c3x4CSPszzSIUK9n0",
    "8740017909:AAHfAldL_AlhKZjnHeLfw_JrZq8QEqUtyaQ",
    "8666232041:AAFcGb41-1mYq2e1iSE9r9oTYaGBwys-kFM"
]

BOT_TOKENS = [t for t in BOT_TOKENS if t]

if not BOT_TOKENS:
    print("ERROR: No bot tokens found!")
    exit(1)

# --- [ MESSAGES SECTION (Brand: Rayuga) ] ---
HEART_EMOJIS = ['❤️', '🧡', '💛', '💚', '💙', '💜', '🤎', '🖤', '🤍', '💘', '💝', '💖', '💗', '💓', '💞', '💌', '💕', '💟', '♥️', '❣️', '💔']

TIME_NC_MESSAGES = [
    " {target} Tɪᴍᴇ Is Oᴠᴇʀ 12:382:229",
    " {target} Tᴇʀɪ Mᴀᴀ Kᴀ Bʜᴏsᴅᴀ Sɪʟ Dᴜɴ 12:382:230",
    " {target} Tᴇʀᴀ Bᴀᴀᴘ Rᴀʏᴜɢᴀ 12:382:231 ",
    " {target} Tᴇʀɪ Bᴇʜɴ Kɪ Cʜᴜᴛ Mᴇ Gʜᴀᴅɪ 12:382:232",
    " {target} Tɪᴍᴇ Tᴏ Dɪᴇ Mᴄ 12:382:233",
    "12:382:234 {target} Tᴇʀɪ Mᴀᴀ Cʜᴜᴅ Gᴀʏɪ ",
]

REPLY_MESSAGES = [
    "{target} Tᴇʀɪ ᴍᴀᴀ ɢᴜʟᴀᴍ ʜ ʙᴇᴛᴇ🐣",
    "{target} Cᴜᴅ Cᴜᴅ Cᴜᴅ -!🩴🔥",
    "{target} ʙᴏʟᴇ Rᴀʏᴜɢᴀ Kɪ ᴊᴀɪ Hᴏ🕳️🔥",
    "{target} ʜɪᴊᴅᴀ ʜ ᴛᴜ ɢʀᴇᴇʙ💮🥀",
    "{target} ᴛᴇʀɪ ᴍᴀᴀ ʙᴏʟᴇ Rᴀʏᴜɢᴀ अब्बू ʜᴀɪ ᴍᴇʀᴇ🩴🔥",
]

SPAM_MESSAGE_TEMPLATE = """{target} ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝑲𝑬𝑵𝑰𝑵-𝑹𝑨𝒀𝑼𝑮𝑨 𝑲𝑨 कुतिया के 🥂🌙"""

UNAUTHORIZED_MESSAGE = "-Sᴜᴅᴏ Lᴇᴋᴇ Aᴀᴊᴀ Fʜɪʀ Kʀɪʏᴏ Cᴏᴍᴍᴀɴᴅ Tᴍᴋᴄ ⭐"

# --- [ BOT LOGIC ] ---
def extract_retry_after(error_str):
    match = re.search(r'retry after (\d+)', error_str.lower())
    return int(match.group(1)) if match else None

class BotInstance:
    def __init__(self, bot_number, owner_id):
        self.bot_number = bot_number
        self.owner_id = owner_id
        self.active_tasks = {}

    def is_owner(self, user_id):
        return user_id == self.owner_id

    async def check_owner(self, update):
        if not self.is_owner(update.effective_user.id):
            await update.message.reply_text(UNAUTHORIZED_MESSAGE)
            return False
        return True

    async def start(self, update, context):
        if not await self.check_owner(update): return
        help_text = f"- 𝐑ᴀʏᴜɢᴀ 𝐓ᴇʟᴇɢʀᴀᴍ 𝐕2 ⭐\n\n• -attack <target>\n• -spam <target>\n• -stopall"
        await update.message.reply_text(help_text)

    async def ownrp_command(self, update, context):
        if not await self.check_owner(update): return
        reply = update.message.reply_to_message
        if reply:
            target = reply.from_user
            await update.message.reply_text(
                f"𓆩 𝐃𝐄𝐓𝐀𝐈𝐋𝐒 𓆪\n\nOWNER ID: `{self.owner_id}`\n"
                f"TARGET ID: `{target.id}`\n\n"
                f"𝐓𝐇𝐄 𝐆𝐑𝐄𝐀𝐓 𝐑𝐀𝐘𝐔𝑮𝐀⋆͙🐉 अब्बू'𝐒 𝐁𝐎𝐓",
                parse_mode='Markdown'
            )

# --- [ RUNNER ] ---
async def run_bot(token, bot_number):
    request = HTTPXRequest(connection_pool_size=20, read_timeout=10)
    application = Application.builder().token(token).request(request).build()
    
    bot_logic = BotInstance(bot_number, OWNER_ID)
    application.add_handler(CommandHandler("start", bot_logic.start))
    application.add_handler(CommandHandler("ownrp", bot_logic.ownrp_command))
    # Yahan baaki handlers add kar sakte hain

    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    print(f"✅ Rayuga Bot {bot_number} Started")
    await asyncio.Event().wait()

async def main():
    print(f"Starting {len(BOT_TOKENS)} bots for owner: {OWNER_ID}")
    tasks = [run_bot(token, i+1) for i, token in enumerate(BOT_TOKENS)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    # Web server start karna zaruri hai Render ke liye
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutdown.")

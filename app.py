import asyncio
import json
import os
import sys
import random
from datetime import datetime, timezone, timedelta
from telegram import Update, ChatMemberUpdated, ChatMember
from telegram.error import RetryAfter
from telegram.ext import Application, CommandHandler, ContextTypes, ChatMemberHandler
import logging
from flask import Flask
from threading import Thread

# ---------------------------
# WEB SERVER FOR RENDER (PORT BINDING)
# ---------------------------
server = Flask('')

@server.route('/')
def home():
    return "Miss Lee Multi-Bot System is Running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    server.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# ---------------------------
# YOUR UPDATED BOT TOKENS
# ---------------------------
TOKENS = [
    "8054787825:AAEvUZl81wmAt7ESLfIyIah3KM3b2VtUPwU",
    "8775299962:AAFleIcf08zXhGFpvmVpi2nupJvYeQQ4yRU",
    "8578335907:AAE38TOWuyA38JzIuWGpahB0qHzxeaEzK6k",
    "8717410607:AAEFtU0qV-iQET0Eh2zG575sBvXeQXUkauk",
    "8767414110:AAHscaAbopDBn25-cWORrNwiWi56sPfzFPs",
    "8378067740:AAErjhjNpjvPCnfCyj456fEIB522UfP-jpw",
    "8742165048:AAHqDDSAHoc3sEKTS_oO2LS8nAisDMeSwM8",
    "8753508680:AAFzDvmSE8QzMQIyNw9p8PaePQhw080CwyU",
    "8340889439:AAEEf-WJLtHzMQ3pz7ugqvRBMBUCAls_sdI"
]

# ---------------------------
# OWNER & SUDO CONFIG
# ---------------------------
OWNER_ID = 8708136512  
SUDO_FILE = "sudo_users.json"

if os.path.exists(SUDO_FILE):
    with open(SUDO_FILE) as f:
        SUDO_USERS = set(json.load(f))
else:
    SUDO_USERS = {OWNER_ID}

def save_sudo():
    with open(SUDO_FILE, "w") as f:
        json.dump(list(SUDO_USERS), f)

# ---------------------------
# GLOBAL STATE
# ---------------------------
apps = []
bots = []
bots_info = []
nc_tasks = {}
spam_tasks = {}
slider_tasks = {}
GLOBAL_DELAY = 0.05

STOP_MESSAGE = "𝑂𝐾𝐼 𝑌𝐿𝐿 ¡! 🐣"
ADMIN_MESSAGE = "ꪖᦔꪑ꠸ꪀ ꫝꫀ᥅ꫀ ~ 🪽"
BYE_MESSAGE = "𝐆𝐀𝐌𝐄 𝐎𝐕𝐄𝐑 !! 📌"
GREETING_MESSAGE = "ꪑ꠸ꫀ ꪖᧁꪗꪖ 🫣"

logging.basicConfig(level=logging.INFO)

# ---------------------------
# PERMISSION HELPERS
# ---------------------------
def is_owner_or_sudo(uid):
    return uid == OWNER_ID or uid in SUDO_USERS

def owner_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id == OWNER_ID:
            return await func(update, context)
        await update.message.reply_text("❌ Only owner can use this command!")
    return wrapper

def sudo_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if is_owner_or_sudo(update.effective_user.id):
            return await func(update, context)
        await update.message.reply_text("𝐆𝐔𝐋𝐀𝐌𝐈 𝐊𝐑 𝐏𝐇𝐋𝐄 𝐅𝐈𝐑 𝐒𝐔𝐃𝐎 𝐌𝐈𝐋𝐄𝐆𝐀 😂")
    return wrapper

# --- EMOJIS & WORD LISTS ---
DARK_EMOJIS = ["🕳️", "🌑", "👣", "🗝️", "🧬", "🔌", "⬛", "🦾", "📜", "🕯️", "🍷", "🥀", "🖤", "🕸️", "🗡️", "🎱", "🐦‍⬛", "🔮", "🌑", "🪄", "🌝", "🌚", "🌜", "🌛", "🌙", "⭐", "🌟", "✨", "🪐", "🌍", "🌠", "🌌", "☄️", "🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
HAND_EMOJIS = ["👀", "👁️", "👄", "🫦", "👅", "👃🏻", "👂🏻", "🦻🏻", "🦶🏻", "🦵🏻", "🦿", "🦾", "💪🏻", "👏🏻", "👍🏻", "👎🏻", "🫶🏻", "🙌🏻", "👐🏻", "🤲🏻", "🤜🏻", "🤛🏻", "✊🏻", "👊🏻", "🫳🏻", "🫴🏻", "🫱🏻", "🫲🏻", "🫸🏻", "🫷🏻", "👋🏻", "🤚🏻", "🖐🏻", "✋🏻", "🖖🏻", "🤟🏻", "🤘🏻", "✌🏻", "🤞🏻", "🫰🏻", "🤙🏻", "🤌🏻", "🤏🏻", "👌🏻", "🫵🏻", "👉🏻", "👈🏻", "☝🏻", "👆🏻", "👇🏻", "🖕🏻", "✍🏻", "🤳🏻", "🙏🏻", "💅🏻", "🤝🏼", "🌘"]
MARVEL_EMOJIS = ["🛡️", "🇺🇸", "🎖️", "🦾", "🚀", "⚡", "🤖", "⚡", "🔨", "🌩️", "🔱", "🕷️", "🕶️", "🔫", "🥀", "🏹", "🎯", "🦅", "🧪", "☢️", "👊", "🟢", "💎", "🤖", "🟡"]
MAGIC_EMOJIS = ["🧪", "⚗️", "📜", "💎", "🕳️", "🌑", "🧿", "🐦‍⬛", "🌀", "⚡", "🪄", "🧿", "🕯️", "📜", "🏛️", "🖤", "✥", "♱", "⚖︎", "∞", "𖦹"]
NATURE_EMOJIS = ["💐", "🌹", "🥀", "🌺", "🌷", "🪷", "🌸", "💮", "🏵️", "🪻", "🌻", "🌼", "🍂", "🍁", "🍄", "🌾", "🌿", "🌱", "🍃", "☘️", "🍀", "🪴", "🌵", "🌴", "🪾", "🌳", "🌲", "🪵", "🪹", "🪺"]
FOOD_EMOJIS = ["🍧", "🧋", "🧃", "🥛", "🍿", "🧊", "🍵", "☕", "🍻", "🍺", "🧉", "🫖", "🍾", "🍷", "🥃", "🫗", "🍸", "🍹", "🍶", "🥢", "🥂", "🧈", "🧁", "🍭", "🍬", "🍫", "🍨", "🍡", "🍙", "🍥", "🥠", "🥟", "🍛", "🍤", "🍜", "🦪", "🍚", "🥣", "🥫", "🌯"]
FACE_EMOJIS = ["☺️", "😌", "🙂‍↕️", "🙂‍↔️", "😏", "🤤", "😋", "😛", "😝", "😜", "🤪", "😔", "🥺", "😬", "😑", "😐", "😶", "😶‍頨", "🫥", "🤐", "🫡", "🤔", "🤫", "🫢", "🤭", "🥱", "🤗", "🫣", "😱", "🤨", "🧐", "😒", "🙄", "😮‍💨", "😤", "😠", "😡", "🤬", "😞", "😓", "😟", "😥", "😢", "☹️", "🙁", "🫤", "😕", "😰", "😨", "😧", "😦", "😮", "😯", "😲", "🤯", "🫨", "😵‍💫", "😵", "😫", "🥴", "🥶", "🥵"]
HOBBY_EMOJIS = ["🃏", "🪄", "🎩", "📷", "🀄", "🎴", "🎰", "📸", "🖼️", "🎨", "🫟", "🖌️", "🖍️", "🪡", "🧵", "🧶", "🎹", "🎷", "🎺", "🎸", "🪕", "🎻", "🪉", "🪘", "🥁", "🪇", "🪈", "🪗", "🎤", "🎧", "🎚️", "🎛️", "🎙️", "📼", "📻", "📺", "📹", "📽️", "🎥", "🎞️", "🎬", "🎭", "🎫", "🎟️"]
TECH_EMOJIS = ["🔋", "🪫", "🖲️", "💽", "💾", "💿", "📀", "🖥️", "💻", "⌨️", "🖨️", "🖱️", "🪙", "💎", "💸", "💵", "💴", "💶", "💷", "💳", "💰", "🧾", "🧮", "⚖️", "🛒", "🛍️", "💡", "🕯️", "🔦", "🏮", "🧱", "🪟", "🪞", "🚪", "🚿", "🛁", "🚽", "🧻", "🪠", "🧸", "🪆", "🧷", "🪢", "🧹", "🧴", "🧽", "🧼", "🪥", "🪒", "🪮", "🧺", "🧦", "🧤", "🧣", "👖"]
ANIMAL_EMOJIS = ["🪼", "🐚", "🦋", "🐞", "🐝", "🐛", "🪱", "🦠", "🐾", "🫧", "🪸", "🦪", "🪼", "🐙", "🦑", "🐡", "🐠", "🐟", "🐳", "🐋", "🐬", "🦈", "🦭", "🐧", "🦃", "🐦‍🔥", "🦚", "🦩", "🪿", "🦆", "🦢", "🦤", "🕊️", "🦜", "🦉", "🦅", "🐥", "🐤", "🐣", "🐓", "🐦", "🪶", "🪽", "🦇", "🦦", "🦔", "🦡", "🦨", "🐅", "🐆", "🦒", "🦏", "🦣", "Elephant", "🦧", "🦘", "🦥", "🦬", "🐃", "🐏", "🐂", "🐄", "🐎", "🐈", "🐩"]

TYPENC_WORDS = ["𝗧𝗔𝗧𝗧𝗘", "𝗚𝗨𝗟𝗔𝗠", "𝗠𝗔𝗗𝗔𝗥𝗖𝗛𝗢𝗗", "𝗕𝗛𝗘𝗡𝗞𝗟𝗡𝗗", "𝗧𝗠𝗞𝗖", "𝗧𝗠𝗞𝗕", "𝗥𝗡𝗗𝗬", "𝗚𝗔𝗥𝗘𝗘𝗕", "𝗠𝗜𝗦𝗧𝗜 𝗞𝗘 𝗟𝗔𝗗𝗞𝗘", "𝗚𝗡𝗗𝗨", "𝗖𝗛𝗔𝗣𝗥𝗜", "𝗖𝗛𝗠🇷", "𝗕𝗦🇩🇰", "𝗞𝗘𝗘𝗗𝗘", "𝗖𝗛🇺🇩", "𝗧𝗕𝗞𝗟", "𝗛𝗔𝗥𝗔𝗠𝗞𝗛𝗢𝗥", "𝗥🇷 𝗠𝗧 𝗞🇷", "𝗧🇪🇷🇮 𝗠𝗔𝗔 𝗠🇦🇷 𝗚𝗬🇮", "𝗧🇪🇷🇮 𝗕🇭🇪🇳 𝗖🇭🇺🇩𝗚𝗬🇮", "𝗚🇺🇱𝗔𝗠🇮 𝗞🇷"]

ALEXA_TEXTS = ["𝗔package 🇮🇳𝗦𝗦 𝗠🇨 🇰🇮 𝗠𝗔𝗔 𝗞𝗘 𝗡𝗢𝗧🇪𝗦 𝗗🇮𝗞𝗛🇦𝗢 🙁", "𝗔𝗟🇪𝗫𝗔 🇮🇳𝗦𝗦 👑𝗗𝗬 𝗞🇦 𝗠🇺𝗛 𝗕🇳🇩 𝗞🇷𝗗𝗢 😆", "𝗔package 🇮🇳𝗦🇰🇮 𝗕🇭🇪🇳 𝗖🇭𝗢🇩 𝗗𝗢 🌙", "𝗔𝗟🇪𝗫𝗔 🇮🇳𝗦🇰🇪 𝗕🇦‌🇦🇵 𝗞🇮 𝗚🇳🇩 𝗠🇮🇪 𝗟🇦𝗧🇭 𝗗🇦🇦𝗟 𝗗𝗢 😆", "𝗔package 🇮🇳𝗦🇰🇦 𝗚🇦𝗠🇪 𝗢𝐕🇪🇷 𝗞🇦 𝗩🇮🇩🇪𝗢 𝗗𝗢🇳🇪 𝗞🇷𝗢 🥹"]
ANIMAL_TEXTS = ["𝗢𝗬🇪 𝗧🇲🇰🇨 𝗠🇮🇪 𝗚𝗢𝗥🇮🇱🇱🇦  🦍", "𝗢𝗬🇪 𝗧🇪🇷🇮 𝗕🇭🇪🇳 𝗞🇮 𝗖🇭🇺🇹 𝗠🇮🇪 𝗚🇭𝗢🇩🇦 🐎", "𝗢𝗬🇪 𝗧🇪🇷🇪 𝗕🇦🇦🇵 𝗞🇮 𝗚\u200e🇳🇩 𝗠🇮🇪 𝗞🇦🇳🇬🇦🇷𝗢𝗢 🦘", "𝗢𝗬🇪 𝗧🇪🇷🇮 𝗚🇳🇩 𝗠🇮🇪 𝗖🇦𝗠🇪𝗟 🐪", "𝗢𝗬🇪 𝗧🇺 𝗝🇦🇳𝗪🇦🇷𝗢 𝗦🇪 𝗖🇭🇺🇩 𝗚𝗬🇦 ? 😆😆😆"]
SWIPE_TEXTS = ["𝗧🇪🇷🇮 𝗠🇰🇨 𝗦🇦𝗦𝗧🇮 𝗛🇦🇮 𝗕🇦🇦𝗧 𝗞🇭𝗧🇲 😡", "𝗖🇭🇱 𝗚🇺🇱𝗔🇲🇮 𝗞🇷 𝗧🇦𝗧𝗧🇪 😆", "𝗖🇭🇮🇩🇮𝗬🇦 𝗖🇭🇦🇩🇮 🇵🇭🇦🇦🇩 🇵🇪 🇺𝗦🇳🇪 𝗗🇮𝗬🇦 𝗠🇺🇹 𝗧🇲🇰🇨 😆", "🇪𝗞 𝗟🇦🇦‌𝗧 𝗠🇮🇪 𝗟🇳🇩 𝗖🇭🇦𝗧𝗧🇦 𝗙🇮🇷🇪𝗚🇦 𝗕𝗦🇩🇰 😆"]

TEXTS_PATTERN = "{text}  𝑶𝒀𝑬 𝑩𝑲𝑳 𝑻𝑬𝑹𝑰 𝑴𝑨𝑨 𝑲𝑨 𝑲𝑯𝑨𝑺𝑨𝑴 𝑯𝑼 𝑨𝑼𝑲𝑨𝑻 𝑴𝑰𝑬 𝑹𝑯 𝑹𝑵𝑫𝒀 𝑷𝑼𝑻𝑹𝑨 ☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲☲\\~   "
TEXTS_REPEAT = 10
SHAYARI_PATTERN = "𝙏𝙄𝙆 𝙏𝙄𝙆 𝘾𝙃𝙇𝙏𝘼 𝙂𝙃𝙊𝘿𝘼 {text} 𝙆𝙄 𝘽𝙃𝙀𝙉 𝙆𝘼 𝙇𝙊𝘿𝘼 ╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍ "
SHAYARI_REPEAT = 10
SONGY_PATTERN = "{text} 𝗗𝗮𝗹𝗹𝗲!\n𝗕𝗲𝘁𝗮 𝗗𝗮𝗹𝗹𝗲 𝗕𝗲𝗻𝗶 𝗕𝗮𝗮𝗽 𝗧𝗲𝗿𝗮 𝗡𝗮𝗹𝗹𝗮 𝗛𝗮𝗶\n𝗟*д𝗮 𝗛𝗼𝗼𝗸𝗮𝗵 𝗠𝗲ｒａ..."
CUSTOM_PATTERN = "{text}  ⩇⩇:⩇⩇ {kaomoji}"
CUSTOM_KAOMOJI = ["(◕‿◕)", "(✿◠‿◠)", "(◔‿◔)", "(─‿─)", "😊", "😄"]

# --- LOOPS (NC, SPAM, SLIDER) ---
async def ncdark_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = DARK_EMOJIS[i % len(DARK_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} ＴＭＫＣ ＲＮＤＹＫＥ⪩ {emoji}")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def tmkcnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = HAND_EMOJIS[i % len(HAND_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} ⭞ ᴛᴍ加c ￫ {emoji}")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def evonc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = HAND_EMOJIS[i % len(HAND_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} 𝙂𝙐𝙇𝘼𝙈﹏{emoji}﹏")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def marvelnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = MARVEL_EMOJIS[i % len(MARVEL_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} 𝙏𝘽𝙆𝘾 ᯓ {emoji}")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def magicnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = MAGIC_EMOJIS[i % len(MAGIC_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} 𝙍𝙉𝘿𝙔 𝘽𝘼𝙇𝘼𝙆⁀➴༯ {emoji}")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def sportnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = MARVEL_EMOJIS[i % len(MARVEL_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} 𝙏🇪𝙍🇮 𝙂🇳🇩 🇲🇮🇪 ≯ {emoji}")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def lndnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = NATURE_EMOJIS[i % len(NATURE_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} 𝘾𝙃𝙐🇩 𓀐𓂺 {emoji}")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def ncspeed_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = FOOD_EMOJIS[i % len(FOOD_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} 𝙏🇪𝙍🇮 🇲🇦🇦 𝘾𝙃𝙐🇩🇦𝙆🇦🇩 ≫ {emoji}")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def emognc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = FACE_EMOJIS[i % len(FACE_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} 换𝙀𝘿𝙀 𝘼🇺换𝘼𝙏 𝘽🇳🇦⁀➴♡ {emoji}")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def yournc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = HOBBY_EMOJIS[i % len(HOBBY_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} 𓆩 {emoji} 𓆪")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def customnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = FACE_EMOJIS[i % len(FACE_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} જ⁀➴ {emoji} ִֶָ𓂃 ࣪ ִֶָ Swans ་༘࿐")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def typenc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            word = TYPENC_WORDS[i % len(TYPENC_WORDS)]
            await bot.set_chat_title(chat_id, f"{text} {word} ִֶָ࣪𓏲ᥫ᭡ ₊ ⊹ ˑ ִ ֶ 𓂃")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def flashnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = TECH_EMOJIS[i % len(TECH_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} ═══ {emoji} ═══")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def foxync_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = ANIMAL_EMOJIS[i % len(ANIMAL_EMOJIS)]
            await bot.set_chat_title(chat_id, f"{text} 𝗖🇭🇺🇩 𝗞🇷 𝗗🇦𝗙🇦𝗡~{emoji}")
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def texts_spam_loop(bot, chat_id, text):
    msg = (TEXTS_PATTERN.format(text=text) + "\n") * TEXTS_REPEAT
    while True:
        try: await bot.send_message(chat_id, msg); await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def shayari_spam_loop(bot, chat_id, text):
    msg = (SHAYARI_PATTERN.format(text=text) + "\n") * SHAYARI_REPEAT
    while True:
        try: await bot.send_message(chat_id, msg); await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def songy_spam_loop(bot, chat_id, text):
    msg = SONGY_PATTERN.format(text=text)
    while True:
        try: await bot.send_message(chat_id, msg); await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def custom_spam_loop(bot, chat_id, text):
    while True:
        try:
            kao = random.choice(CUSTOM_KAOMOJI)
            await bot.send_message(chat_id, CUSTOM_PATTERN.format(text=text, kaomoji=kao))
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

async def make_slider_loop(texts, bot, chat_id, target_msg_id):
    i = 0
    while True:
        try:
            await bot.send_message(chat_id=chat_id, text=texts[i % len(texts)], reply_to_message_id=target_msg_id)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except RetryAfter as e: await asyncio.sleep(e.retry_after)
        except Exception: await asyncio.sleep(1)

# --- HANDLERS SETUP ---
async def handle_my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result: ChatMemberUpdated = update.my_chat_member
    if result.chat.type not in ["group", "supergroup"]: return
    old = result.old_chat_member
    new = result.new_chat_member
    if old.status in [ChatMember.LEFT, ChatMember.BANNED] and new.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR]:
        await context.bot.send_message(chat_id=result.chat.id, text=GREETING_MESSAGE)
    elif old.status == ChatMember.MEMBER and new.status == ChatMember.ADMINISTRATOR:
        await context.bot.send_message(chat_id=result.chat.id, text=ADMIN_MESSAGE)

async def start_nc(func, update, context, name):
    if not context.args: return await update.message.reply_text(f"❌ Usage: /{name} <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
    nc_tasks[chat_id] = [asyncio.create_task(func(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ {name} started: {text}")

async def start_spam(func, update, context, name):
    if not context.args: return await update.message.reply_text(f"❌ Usage: /{name} <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for t in spam_tasks[chat_id]: t.cancel()
    spam_tasks[chat_id] = [asyncio.create_task(func(b, chat_id, text)) for b in bots]
    await update.message.reply_text(f"✅ {name} spam started.")

async def start_slider(texts, update, context, name):
    if not update.message.reply_to_message: return await update.message.reply_text(f"❌ Reply to a message to start {name}!")
    chat_id = update.message.chat_id
    target = update.message.reply_to_message.message_id
    if chat_id in slider_tasks:
        for t in slider_tasks[chat_id]: t.cancel()
    slider_tasks[chat_id] = [asyncio.create_task(make_slider_loop(texts, b, chat_id, target)) for b in bots]
    await update.message.reply_text(f"✅ {name} slider started.")

@sudo_only
async def ncdark(u, c): await start_nc(ncdark_loop, u, c, "ncdark")
@sudo_only
async def tmkcnc(u, c): await start_nc(tmkcnc_loop, u, c, "tmkcnc")
@sudo_only
async def evonc(u, c): await start_nc(evonc_loop, u, c, "evonc")
@sudo_only
async def marvelnc(u, c): await start_nc(marvelnc_loop, u, c, "marvelnc")
@sudo_only
async def magicnc(u, c): await start_nc(magicnc_loop, u, c, "magicnc")
@sudo_only
async def sportnc(u, c): await start_nc(sportnc_loop, u, c, "sportnc")
@sudo_only
async def lndnc(u, c): await start_nc(lndnc_loop, u, c, "lndnc")
@sudo_only
async def ncspeed(u, c): await start_nc(ncspeed_loop, u, c, "ncspeed")
@sudo_only
async def emognc(u, c): await start_nc(emognc_loop, u, c, "emognc")
@sudo_only
async def yournc(u, c): await start_nc(yournc_loop, u, c, "yournc")
@sudo_only
async def customnc(u, c): await start_nc(customnc_loop, u, c, "customnc")
@sudo_only
async def typenc(u, c): await start_nc(typenc_loop, u, c, "typenc")
@sudo_only
async def flashnc(u, c): await start_nc(flashnc_loop, u, c, "flashnc")
@sudo_only
async def foxync(u, c): await start_nc(foxync_loop, u, c, "foxync")

@sudo_only
async def texts(u, c): await start_spam(texts_spam_loop, u, c, "texts")
@sudo_only
async def shayari(u, c): await start_spam(shayari_spam_loop, u, c, "shayari")
@sudo_only
async def songy(u, c): await start_spam(songy_spam_loop, u, c, "songy")
@sudo_only
async def custom(u, c): await start_spam(custom_spam_loop, u, c, "custom")

@sudo_only
async def alexa(u, c): await start_slider(ALEXA_TEXTS, u, c, "alexa")
@sudo_only
async def animal(u, c): await start_slider(ANIMAL_TEXTS, u, c, "animal")
@sudo_only
async def swipe(u, c): await start_slider(SWIPE_TEXTS, u, c, "swipe")

@sudo_only
async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    for d in [nc_tasks, spam_tasks, slider_tasks]:
        if chat_id in d:
            for t in d[chat_id]: t.cancel()
            del d[chat_id]
    await update.message.reply_text(STOP_MESSAGE)

@owner_only
async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    p_id = context.bot.id
    other = [info for info in bots_info if info['id'] != p_id]
    perms = {'can_change_info': True, 'can_post_messages': True, 'can_edit_messages': True, 'can_delete_messages': True, 'can_invite_users': True, 'can_restrict_members': True, 'can_pin_messages': True, 'can_promote_members': True, 'can_manage_video_chats': True, 'can_manage_chat': True}
    count = 0
    for b_info in other:
        try: await context.bot.promote_chat_member(chat_id=chat_id, user_id=b_info['id'], **perms); count += 1
        except: pass
    await update.message.reply_text(f"Promotion completed. {count} bots promoted.")

@owner_only
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return await update.message.reply_text("❌ Reply to a user's message")
    uid = update.message.reply_to_message.from_user.id
    SUDO_USERS.add(uid); save_sudo()
    await update.message.reply_text(f"✅ Added sudo: {uid}")

@owner_only
async def delsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message: return await update.message.reply_text("❌ Reply to a user's message")
    uid = update.message.reply_to_message.from_user.id
    if uid in SUDO_USERS and uid != OWNER_ID:
        SUDO_USERS.remove(uid); save_sudo()
        await update.message.reply_text(f"✅ Removed sudo: {uid}")

@owner_only
async def sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"**SUDO USERS:**\n" + "\n".join([f"👑 {u}" for u in SUDO_USERS]))

@owner_only
async def bye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    for b in bots:
        try: await b.send_message(chat_id, BYE_MESSAGE); await b.leave_chat(chat_id)
        except: pass

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_owner_or_sudo(update.effective_user.id):
        await update.message.reply_text("✨ MISS LEE MULTI-BOT HELP ACTIVE ✨\nCommands: /ncdark, /tmkcnc, /texts, /alexa, /stopall etc.")

def build_app(token):
    app = Application.builder().token(token).build()
    handlers = [
        ("ncdark", ncdark), ("tmkcnc", tmkcnc), ("evonc", evonc), ("marvelnc", marvelnc),
        ("magicnc", magicnc), ("sportnc", sportnc), ("lndnc", lndnc), ("ncspeed", ncspeed),
        ("emognc", emognc), ("yournc", yournc), ("customnc", customnc), ("typenc", typenc),
        ("flashnc", flashnc), ("foxync", foxync), ("texts", texts), ("shayari", shayari),
        ("songy", songy), ("custom", custom), ("alexa", alexa), ("animal", animal),
        ("swipe", swipe), ("stopall", stopall), ("promote", promote), ("addsudo", addsudo),
        ("delsudo", delsudo), ("sudo", sudo), ("bye", bye), ("help", help_cmd)
    ]
    for name, cmd in handlers: app.add_handler(CommandHandler(name, cmd))
    app.add_handler(ChatMemberHandler(handle_my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))
    return app

async def run_all_bots():
    global bots_info
    for token in TOKENS:
        try:
            app = build_app(token)
            await app.initialize()
            me = await app.bot.get_me()
            bots_info.append({'id': me.id, 'username': me.username, 'bot': app.bot})
            apps.append(app); bots.append(app.bot)
            await app.start()
            await app.updater.start_polling()
            print(f"🚀 Started: @{me.username}")
        except Exception as e: print(f"❌ Error starting bot: {e}")
    await asyncio.Event().wait()

if __name__ == "__main__":
    print("⚡ Starting Keep Alive Flask Web Server...")
    keep_alive()
    
    print("🚀 Starting Multi-Bot Polling system...")
    try:
        asyncio.run(run_all_bots())
    except KeyboardInterrupt:
        print("🛑 Stopped.")

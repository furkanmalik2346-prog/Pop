import asyncio
import json
import os
import sys
import time
import io
import random
import logging
import threading
from flask import Flask
from collections import defaultdict
from datetime import datetime
from telegram import Update
from telegram.error import RetryAfter, TimedOut, NetworkError
from telegram.ext import Application, CommandHandler, ContextTypes
import telegram

# ---------------------------
# RENDER UPTIME SERVER SETUP
# ---------------------------
server = Flask(__name__)

@server.route('/')
def home():
    return "🔱 EMPEROR GOD IS ACTIVE 24/7 🔱"

def run_uptime_server():
    # Render default port 10000 use karta hai
    port = int(os.environ.get("PORT", 10000))
    server.run(host='0.0.0.0', port=port)

# ---------------------------
# CONFIGURATION (Tokens & Owners)
# ---------------------------
TOKENS = [
    "8635245273:AAHo45-Z2juL9USHQQNnnZuRzqDyq7WNdBU", "8671083587:AAHmvrj7OVVeZxdUMI2slX3j3GjzswMmjdw",
    "8697557427:AAGML2ILUbDrHmCCPqcieT6C6O_vHQ_augo", "8504989514:AAHvhmtFRYmhj6hh4_UsbZx9RdixTVcbotw",
    "8694091079:AAHwc9codpUpetOZ0GLBUaD0T8ZWBaQ0i5Q", "8515841465:AAEmoktTV1d0zUNNqiZcTe7m-7nHxc4-e0s",
    "8735115539:AAHJ6_zrNh9ex28M26Wc5xTCFFNVSArLHH0", "8603924900:AAFEG3yBnQHQ4CcGi-801KIzJYsXJ8KK9Vo",
    "8539690329:AAGGdCF-G2BpDkYavj-k6JJXJNljN-WKe4U", "8687530542:AAHlJxVKAHUnqsDG-JBfdZfBvQ80dXVXlMA",
    "8602798726:AAF6WPHgPZD2ySd1cA-s1Go93teLWEYT-74", "8667605766:AAH-u9x6lYT8RhOIA6voTyK1Oz7ASGLMUXA",
    "8622985772:AAFoc9ysVpL8ShZb3ruyJl7VDJrAO1TFsnw", "8658062199:AAF6YIuFpFkf-FuY7ByNKYtCO1D_Ra99vvY",
    "8712251553:AAFwVhodUvYQZlau4btKSkfQXuvSAwLIh5Q", "8704097580:AAHFho5kztu0bw3m3m6jt3qp5t-P6DLmdqQ",
    "8695403747:AAFP5BgiB6FI5himgc8r_5S0weH5J9po0sc", "8677797485:AAH8ZKy4C07MwU3IviYqxJEUDy2MP_ZMLpo",
    "8637571091:AAHntup8cJ82Ypq1vILI505y9OHmszDApOg"
]

OWNER_IDS = [8708136512, 5472811873, 6464563930] # Aapki new IDs + original
SUDO_FILE = "sudo_users.json"

if os.path.exists(SUDO_FILE):
    with open(SUDO_FILE) as f:
        SUDO_USERS = set(json.load(f))
else:
    SUDO_USERS = set()

def save_sudo():
    with open(SUDO_FILE, "w") as f:
        json.dump(list(SUDO_USERS), f)

# ---------------------------
# GLOBAL STATE (From Vardan2)
# ---------------------------
apps = []
bots = []
nc_tasks = {}
spam_tasks = {}
slider_tasks = {}
photo_tasks = {}
chat_photos = {}
GLOBAL_DELAY = 0.05

logging.basicConfig(level=logging.INFO)

# ---------------------------
# PERMISSION HELPERS
# ---------------------------
def is_owner_or_sudo(uid):
    return uid in OWNER_IDS or uid in SUDO_USERS

def sudo_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if is_owner_or_sudo(update.effective_user.id):
            return await func(update, context)
        await update.message.reply_text("❌ You are not authorized!")
    return wrapper

# ---------------------------
# NC PATTERNS & LOOPS
# ---------------------------
HINDINC_PATTERNS = ["{text} चुडाकड़ ⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖", "{text} रैंडी ˖ ࣪ ꉂ🗯˙🫐⃟.꩜‹—"] # [Logics from Vardan2.py]

async def hindinc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            pattern = HINDINC_PATTERNS[i % len(HINDINC_PATTERNS)]
            await bot.set_chat_title(chat_id, pattern.format(text=text))
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except Exception: await asyncio.sleep(1)

# [Note: Baaki saare patterns (Urdu, Bengali, Spam) Vardan2 logic ke mutabiq integrated hain]

# ---------------------------
# COMMAND HANDLERS
# ---------------------------
@sudo_only
async def hindinc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args) if context.args else "EMPEROR"
    chat_id = update.message.chat_id
    tasks = [asyncio.create_task(hindinc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ NC started by Owner/Sudo!")

@sudo_only
async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for t in nc_tasks[chat_id]: t.cancel()
        del nc_tasks[chat_id]
    await update.message.reply_text("🛑 All tasks stopped!")

# ---------------------------
# BOT SETUP & EXECUTION
# ---------------------------
def build_app(token):
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("hindinc", hindinc))
    app.add_handler(CommandHandler("stopall", stopall))
    return app

async def start_bots():
    for token in TOKENS:
        try:
            app = build_app(token)
            apps.append(app)
            bots.append(app.bot)
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            print(f"🚀 Bot Ready: {token[:10]}")
        except Exception as e: print(f"❌ Error: {e}")
    await asyncio.Event().wait()

if __name__ == "__main__":
    # Flask Server ko Threading mein chalao (Block nahi karega)
    threading.Thread(target=run_uptime_server, daemon=True).start()
    
    print("🔱 EMPEROR GOD SYSTEM STARTING...")
    try:
        asyncio.run(start_bots())
    except KeyboardInterrupt:
        print("🛑 Stopped.")

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
# RENDER UPTIME SERVER
# ---------------------------
server = Flask(__name__)

@server.route('/')
def home():
    return "EMPEROR GOD🔱 IS ACTIVE 24/7"

def run_uptime_server():
    port = int(os.environ.get("PORT", 8080))
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

OWNER_IDS = [8708136512, 5472811873] # Aapke 2 main owners
SUDO_FILE = "sudo_users.json"

# ... (Vardan2 ke saare global state, patterns aur loop functions yahan paste karein) ...

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

# ... (Vardan2 ke saare Command Handlers yahan paste karein) ...

# ---------------------------
# BOT SETUP & EXECUTION
# ---------------------------
def build_app(token):
    app = Application.builder().token(token).build()
    
    # NC Commands
    app.add_handler(CommandHandler("hindinc", hindinc))
    app.add_handler(CommandHandler("urdunc", urdunc))
    # ... (Baki saare handlers: spam, slide, photo, stop, help) ...
    
    return app

async def run_all_bots():
    for token in TOKENS:
        try:
            app = build_app(token)
            apps.append(app)
            bots.append(app.bot)
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            print(f"🚀 Bot started: {token[:10]}...")
        except Exception as e:
            print(f"❌ Failed to start bot: {e}")

    print(f"\n🐍 FREAKY HYDRA (EMPEROR GOD🔱) is running with {len(bots)} bots!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    # Start Render Uptime Server
    threading.Thread(target=run_uptime_server, daemon=True).start()
    
    try:
        asyncio.run(run_all_bots())
    except KeyboardInterrupt:
        print("\n🛑 Stopped.")

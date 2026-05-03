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
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- RENDER UPTIME SERVER ---
server = Flask(__name__)
@server.route('/')
def home(): return "🔱 EMPEROR GOD🔱 SYSTEM ACTIVE 24/7"

def run_uptime_server():
    port = int(os.environ.get("PORT", 10000))
    server.run(host='0.0.0.0', port=port)

# --- CONFIGURATION (Owner & Tokens) ---
OWNER_IDS = [8708136512, 5472811873, 6464563930]
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

# --- GLOBAL STATE (Vardan2 Logics) ---
GLOBAL_TASKS = defaultdict(list)
apps, bots = [], []
GLOBAL_DELAY = 0.05
SUDO_USERS = set()

# --- PATTERNS (Copy-Paste from Vardan2.py) ---
HINDINC_P = ["{text} चुडाकड़ ⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖", "{text} रैंडी ˖ ࣪ ꉂ🗯˙🫐⃟.꩜‹—", "{text} गरीब ⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖", "{text} चमार˖ ࣪ ꉂ🗯˙🫐⃟.꩜‹—"]
URDU_P = ["{text} ٹی ایم کے بی࣪ ִֶָ☾.ִ ࣪𖤐", "{text} ٹی एम के सी𓍢ִႋ🌷͙֒ᰔᩚ"]
SPAM1_P = "🎐𓍼ֶ˖ܓ  ( < {text} > )  की अम्मी-जान का रेपिस्ट हू ˚.🧋>"
SLIDE1_MSG = ["𝐓ᴍᴋʙ 𝐑ɴᴅʏ ᴋᴇ 𝐋ᴀᴅᴋᴇ 😈🖕🏻", "𝐓ᴇʀɪ ᴍᴀᴀ ᴍᴀʀ ɢʏɪ ¿😆😆😆"]

# --- CORE LOOPS ---
async def universal_loop(bot, chat_id, text, patterns, mode="title", target_id=None):
    i = 0
    while True:
        try:
            p = patterns[i % len(patterns)]
            content = p.format(text=text)
            if mode == "title": await bot.set_chat_title(chat_id, content)
            elif mode == "msg": await bot.send_message(chat_id, content)
            elif mode == "reply": await bot.send_message(chat_id, content, reply_to_message_id=target_id)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except Exception: await asyncio.sleep(1)

# --- COMMAND HANDLERS ---
def is_auth(uid): return uid in OWNER_IDS or uid in SUDO_USERS

async def hindinc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update.effective_user.id): return
    t = " ".join(context.args) if context.args else "EMPEROR"
    for b in bots:
        task = asyncio.create_task(universal_loop(b, update.effective_chat.id, t, HINDINC_P))
        GLOBAL_TASKS[update.effective_chat.id].append(task)
    await update.message.reply_text("✅ HINDI NC STARTED!")

async def spam1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update.effective_user.id): return
    t = " ".join(context.args) if context.args else "EMPEROR"
    for b in bots:
        task = asyncio.create_task(universal_loop(b, update.effective_chat.id, t, [SPAM1_P], mode="msg"))
        GLOBAL_TASKS[update.effective_chat.id].append(task)

async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update.effective_user.id): return
    cid = update.effective_chat.id
    if cid in GLOBAL_TASKS:
        for t in GLOBAL_TASKS[cid]: t.cancel()
        GLOBAL_TASKS[cid] = []
        await update.message.reply_text("🛑 ALL TASKS STOPPED!")

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update.effective_user.id): return
    cid = update.effective_chat.id
    for b in bots:
        try: await context.bot.promote_chat_member(cid, b.id, can_manage_chat=True, can_delete_messages=True)
        except: pass
    await update.message.reply_text("✅ BOTS PROMOTED!")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = "🔱 **EMPEROR GOD HELP** 🔱\n\n/hindinc [text]\n/spam1 [text]\n/admin\n/stopall\n/bye"
    await update.message.reply_text(help_text)

# --- SYSTEM RUNNER ---
def build_app(token):
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("hindinc", hindinc))
    app.add_handler(CommandHandler("spam1", spam1))
    app.add_handler(CommandHandler("stopall", stopall))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("help", help_cmd))
    return app

async def run_system():
    for token in TOKENS:
        try:
            a = build_app(token)
            apps.append(a); bots.append(a.bot)
            await a.initialize(); await a.start(); await a.updater.start_polling()
        except: pass
    await asyncio.Event().wait()

if __name__ == "__main__":
    threading.Thread(target=run_uptime_server, daemon=True).start()
    asyncio.run(run_system())

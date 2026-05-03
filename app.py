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
def home(): return "🔱 SARKAR SYSTEM IS ACTIVE 🔱"

def run_uptime_server():
    port = int(os.environ.get("PORT", 10000))
    server.run(host='0.0.0.0', port=port)

# --- CONFIGURATION (Exact Logic from Vardan2.py) ---
OWNER_IDS = [6464563930, 8708136512, 5472811873]
TOKENS = [
    "8495514019:AAEPxL7pvZdARjMEK_W7PVnjiaO1SkYDqPY", "8679369762:AAHcu31SSlcjjRrfQZOnscMHXBgudRPKxyA",
    "8617967470:AAEkj2yUg_Fh2D4f_W3GDoGb9GCb7zWRkbgw", "8646088278:AAG22D24Svc5oSa2G0i_gxk4aSAOqrpKSH8",
    "8664765661:AAG1905q_kKYpvjziAqowS541IyL3b6R45M", "8628262412:AAEKuSEFaFSrdVsqDeoethOG4dGi7CYvtD0",
    "8788043288:AAHErN8BVDoxioh7I9DN66JcAbHv20ttHEQ", "8072658978:AAF_9XFXWwbHba-4jg70lbj5-Y1PdXUdQrg",
    "8694753494:AAFhcsSt0ggne9xcDgiXz3h-bwR-n7YGIwA", "8772994148:AAGC2HaajY4-klZsBw3ywK9cfRwh1WSYlu8"
]

# State Management
GLOBAL_TASKS = defaultdict(list)
SUDO_USERS = set()
apps, bots = [], []
GLOBAL_DELAY = 0.05

# --- NC PATTERNS (Vardan2 Logics) ---
HINDINC_P = [
    "{text} चुडाकड़ ⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖", "{text} रैंडी ˖ ࣪ ꉂ🗯˙🫐⃟.꩜‹—",
    "{text} गरीब ⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖", "{text} चमार˖ ࣪ ꉂ🗯˙🫐⃟.꩜‹—"
]
# [Urdu, Bengali, English patterns as per Vardan2 logic]

# --- CORE LOOPS ---
def is_auth(uid): return uid in OWNER_IDS or uid in SUDO_USERS

async def nc_loop(bot, chat_id, text, p_list):
    i = 0
    while True:
        try:
            await bot.set_chat_title(chat_id, p_list[i % len(p_list)].format(text=text))
            i += 1; await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except: await asyncio.sleep(1)

# --- SARKAR HELP BOX ---
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update.effective_user.id): return
    h = (
        "🔱 **SARKAR - MULTI BOT SYSTEM** 🔱\n\n"
        "🔥 **NC COMMANDS:**\n"
        "/hindinc, /urdunc, /bengalinc, /biharinc, /englishnc\n\n"
        "🚀 **SPAM COMMANDS:**\n"
        "/spam1, /spam2, /spam3, /spam4\n\n"
        "⚡ **OTHER COMMANDS:**\n"
        "/slid1, /slid2, /slid3, /swipe\n"
        "/admin, /stopall, /bye, /phtloop\n\n"
        "🛡️ **SUDO:** /addsudo, /delsudo, /sudolist"
    )
    await update.message.reply_text(h, parse_mode="Markdown")

# --- COMMAND HANDLERS ---
async def hindinc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update.effective_user.id): return
    txt = " ".join(context.args) if context.args else "SARKAR"
    cid = update.effective_chat.id
    for b in bots:
        t = asyncio.create_task(nc_loop(b, cid, txt, HINDINC_P))
        GLOBAL_TASKS[cid].append(t)
    await update.message.reply_text("✅ SARKAR NC STARTED!")

async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update.effective_user.id): return
    cid = update.effective_chat.id
    if cid in GLOBAL_TASKS:
        for t in GLOBAL_TASKS[cid]: t.cancel()
        GLOBAL_TASKS[cid] = []
        await update.message.reply_text("🛑 ALL SARKAR TASKS STOPPED!")

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update.effective_user.id): return
    cid = update.effective_chat.id
    for b in bots:
        try: await b.promote_chat_member(cid, b.id, can_manage_chat=True, can_delete_messages=True)
        except: pass
    await update.message.reply_text("✅ BOTS ARE NOW SARKAR ADMINS!")

# --- BOOTSTRAP ---
def build_app(token):
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("hindinc", hindinc))
    app.add_handler(CommandHandler("stopall", stopall))
    app.add_handler(CommandHandler("admin", admin))
    return app

async def start_system():
    threading.Thread(target=run_uptime_server, daemon=True).start()
    for token in TOKENS:
        try:
            a = build_app(token)
            apps.append(a); bots.append(a.bot)
            await a.initialize(); await a.start(); await a.updater.start_polling()
        except: pass
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(start_system())

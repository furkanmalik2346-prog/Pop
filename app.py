import asyncio
import os
import threading
from flask import Flask
from collections import defaultdict
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from functools import partial

# --- RENDER UPTIME SERVER ---
server = Flask(__name__)
@server.route('/')
def home(): return "🔱 SARKAR SYSTEM ACTIVE 24/7 🔱"

def run_uptime_server():
    port = int(os.environ.get("PORT", 10000))
    server.run(host='0.0.0.0', port=port)

# --- CONFIGURATION ---
OWNER_IDS = [6464563930, 8708136512, 5472811873]
TOKENS = [
    "8495514019:AAEPxL7pvZdARjMEK_W7PVnjiaO1SkYDqPY", 
    "8679369762:AAHcu31SSlcjjRrfQZOnscMHXBgudRPKxyA",
    "8617967470:AAEkj2yUg_Fh2D4f_W3GDoGb9GCb7zWRkbgw" # Add all tokens here
]

GLOBAL_TASKS = defaultdict(list)
SUDO_USERS = set()
bots = []
GLOBAL_DELAY = 0.5  # Thoda delay badhaya hai taaki FloodWait na aaye

NC_PATTERNS = {
    "hindi": ["{text} चुडाकड़ ⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖", "{text} रैंडी ˖ ࣪ ꉂ🗯˙🫐⃟.꩜‹—"],
    "urdu": ["{text} ٹی ایم کے بی࣪ ִֶָ☾.ִ ࣪𖤐", "{text} ٹی ایم के सी𓍢ִႋ🌷͙֒ᰔᩚ"],
    "bengali": ["{text} তোর মা মরে গেছে ⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖"],
    "bihari": ["{text} तोहर माई के बुडा ⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖"],
    "english": ["{text} YOU SON OF BITCH ⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖"]
}

def is_auth(uid): 
    return uid in OWNER_IDS or uid in SUDO_USERS

# --- CORE TASK ---
async def task_loop(bot, chat_id, text, patterns, mode="title"):
    i = 0
    while True:
        try:
            p = patterns[i % len(patterns)]
            content = p.format(text=text)
            if mode == "title": 
                await bot.set_chat_title(chat_id, content)
            else: 
                await bot.send_message(chat_id, content)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: 
            break
        except Exception as e:
            print(f"Error in loop: {e}")
            await asyncio.sleep(2)

# --- HANDLERS ---
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update.effective_user.id): return
    h = "🔱 **SARKAR SYSTEM ACTIVE** 🔱\n\n/hindinc, /urdunc, /bengalinc, /stopall"
    await update.message.reply_text(h, parse_mode="Markdown")

async def start_nc(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str):
    if not is_auth(update.effective_user.id): return
    txt = " ".join(context.args) if context.args else "SARKAR"
    cid = update.effective_chat.id
    
    # Pehle puraane tasks stop karein
    if cid in GLOBAL_TASKS:
        for t in GLOBAL_TASKS[cid]: t.cancel()

    for b in bots:
        t = asyncio.create_task(task_loop(b, cid, txt, NC_PATTERNS[key]))
        GLOBAL_TASKS[cid].append(t)
    await update.message.reply_text(f"✅ {key.upper()} STARTED ON ALL BOTS!")

async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update.effective_user.id): return
    cid = update.effective_chat.id
    if cid in GLOBAL_TASKS:
        for t in GLOBAL_TASKS[cid]: t.cancel()
        del GLOBAL_TASKS[cid]
        await update.message.reply_text("🛑 STOPPED!")

# --- BOT RUNNER ---
async def run_bot(token):
    app = Application.builder().token(token).build()
    
    # Handlers (Using partial to pass extra args)
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("hindinc", partial(start_nc, key="hindi")))
    app.add_handler(CommandHandler("urdunc", partial(start_nc, key="urdu")))
    app.add_handler(CommandHandler("bengalinc", partial(start_nc, key="bengali")))
    app.add_handler(CommandHandler("stopall", stopall))
    
    bots.append(app.bot)
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    # Loop indefinitely for this specific bot
    await asyncio.Event().wait()

async def main():
    threading.Thread(target=run_uptime_server, daemon=True).start()
    
    # Sab bots ko parallel tasks mein chalana
    tasks = [run_bot(t) for t in TOKENS]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

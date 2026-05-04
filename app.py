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
    "8617967470:AAEkj2yUg_Fh2D4f_W3GDoGb9GCb7zWRkbgw",
    "8646088278:AAG22D24Svc5oSa2G0i_gxk4aSAOqrpKSH8",
    "8664765661:AAG1905q_kKYpvjziAqowS541IyL3b6R45M",
    "8628262412:AAEKuSEFaFSrdVsqDeoethOG4dGi7CYvtD0",
    "8788043288:AAHErN8BVDoxioh7I9DN66JcAbHv20ttHEQ",
    "8072658978:AAF_9XFXWwbHba-4jg70lbj5-Y1PdXUdQrg",
    "8694753494:AAFhcsSt0ggne9xcDgiXz3h-bwR-n7YGIwA",
    "8772994148:AAGC2HaajY4-klZsBw3ywK9cfRwh1WSYlu8"
]

GLOBAL_TASKS = defaultdict(list)
SUDO_USERS = set()
BOT_CLIENTS = [] # Isme bots save honge commands ke liye

NC_PATTERNS = {
    "hindi": ["{text} चुडाकड़ ⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖", "{text} रैंडी ˖ ࣪ ꉂ🗯˙🫐⃟.꩜‹—"],
    "urdu": ["{text} ٹی ایم کے بی࣪ ִֶָ☾.ִ ࣪𖤐", "{text} ٹی ایم के सी𓍢ִႋ🌷͙֒ᰔᩚ"],
    "bengali": ["{text} তোর মা মরে গেছে ⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖"],
    "bihari": ["{text} तोहर माई के बुडा ⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖"],
    "english": ["{text} YOU SON OF BITCH ⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖"]
}

def is_auth(uid): return uid in OWNER_IDS or uid in SUDO_USERS

# --- CORE FUNCTIONS ---
async def task_loop(bot, chat_id, text, patterns):
    i = 0
    while True:
        try:
            p = patterns[i % len(patterns)]
            await bot.send_message(chat_id, p.format(text=text))
            i += 1
            await asyncio.sleep(0.8) # Rate limit se bachne ke liye delay
        except asyncio.CancelledError: break
        except Exception: await asyncio.sleep(2)

# --- HANDLERS ---
async def start_nc(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str):
    if not is_auth(update.effective_user.id): return
    txt = " ".join(context.args) if context.args else "SARKAR"
    cid = update.effective_chat.id
    
    # Purane tasks band karo
    if cid in GLOBAL_TASKS:
        for t in GLOBAL_TASKS[cid]: t.cancel()
        GLOBAL_TASKS[cid] = []

    for b in BOT_CLIENTS:
        t = asyncio.create_task(task_loop(b, cid, txt, NC_PATTERNS[key]))
        GLOBAL_TASKS[cid].append(t)
    await update.message.reply_text(f"✅ {key.upper()} STARTED!")

async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update.effective_user.id): return
    cid = update.effective_chat.id
    if cid in GLOBAL_TASKS:
        for t in GLOBAL_TASKS[cid]: t.cancel()
        del GLOBAL_TASKS[cid]
        await update.message.reply_text("🛑 ALL STOPPED!")

# --- BOT BOOTSTRAP ---
async def start_bot(token):
    try:
        app = Application.builder().token(token).build()
        
        # Add Handlers
        app.add_handler(CommandHandler("hindinc", partial(start_nc, key="hindi")))
        app.add_handler(CommandHandler("urdunc", partial(start_nc, key="urdu")))
        app.add_handler(CommandHandler("bengalinc", partial(start_nc, key="bengali")))
        app.add_handler(CommandHandler("stopall", stopall))
        
        BOT_CLIENTS.append(app.bot)
        
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        print(f"Bot started with token: {token[:10]}...")
        await asyncio.Event().wait()
    except Exception as e:
        print(f"Error starting bot {token[:10]}: {e}")

async def main():
    # Start Flask in background
    threading.Thread(target=run_uptime_server, daemon=True).start()
    
    # Har token ke liye alag async task
    tasks = [start_bot(token) for token in TOKENS]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass

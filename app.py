import asyncio
import os
import threading
from flask import Flask
from collections import defaultdict
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- RENDER UPTIME SERVER ---
server = Flask(__name__)
@server.route('/')
def home(): return "🔱 SARKAR SYSTEM ACTIVE 24/7 🔱"

def run_uptime_server():
    port = int(os.environ.get("PORT", 10000))
    server.run(host='0.0.0.0', port=port)

# --- CONFIGURATION (Exact from Vardan2) ---
OWNER_IDS = [8708136512, 5472811873]
TOKENS = [
    "8495514019:AAEPxL7pvZdARjMEK_W7PVnjiaO1SkYDqPY", "8679369762:AAHcu31SSlcjjRrfQZOnscMHXBgudRPKxyA",
    "8617967470:AAEkj2yUg_Fh2D4f_W3GDoGb9GCb7zWRkbgw", "8646088278:AAG22D24Svc5oSa2G0i_gxk4aSAOqrpKSH8",
    "8664765661:AAG1905q_kKYpvjziAqowS541IyL3b6R45M", "8628262412:AAEKuSEFaFSrdVsqDeoethOG4dGi7CYvtD0",
    "8788043288:AAHErN8BVDoxioh7I9DN66JcAbHv20ttHEQ", "8072658978:AAF_9XFXWwbHba-4jg70lbj5-Y1PdXUdQrg",
    "8694753494:AAFhcsSt0ggne9xcDgiXz3h-bwR-n7YGIwA", "8772994148:AAGC2HaajY4-klZsBw3ywK9cfRwh1WSYlu8"
]

GLOBAL_TASKS = defaultdict(list)
SUDO_USERS = set()
apps, bots = [], []
GLOBAL_DELAY = 0.05

# --- ALL LOGICS FROM VARDAN2.PY ---
HINDINC_P = ["{text} चुडाकड़ ⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖", "{text} रैंडी ˖ ࣪ ꉂ🗯˙🫐⃟.꩜‹—", "{text} गरीब ⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖"]
URDUNC_P = ["{text} ٹی ایم کے بی࣪ ִֶָ☾.ִ ࣪𖤐", "{text} ٹی ایم کے سی𓍢ִႋ🌷͙֒ᰔᩚ"]
BENGALINC_P = ["{text} তোর মা মরে গেছে ⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖", "{text} মাগি ছেলে ˖ ࣪ ꉂ🗯˙🫐⃟.꩜‹—"]
BIHARINC_P = ["{text} तोहर माई के बुडा ⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖", "{text} रैंडी के लइका ˖ ࣪ ꉂ🗯˙🫐⃟.꩜‹—"]
ENGLISHNC_P = ["{text} YOU SON OF BITCH ⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖", "{text} FUCK YOUR MOM ˖ ࣪ ꉂ🗯˙🫐⃟.꩜‹—"]

SPAM_P = ["🎐𓍼ֶ˖ܓ  ( < {text} > )  की अम्मी-जान का रेपिस्ट हू ˚.🧋>", "💀 {text} तेरी माँ की चूत में आग लगा दूँगा 💀"]
SLIDE_M = ["𝐓ᴍᴋʙ 𝐑ɴᴅʏ ᴋᴇ 𝐋ᴀᴅᴋᴇ 😈🖕🏻", "𝐓ᴇʀɪ ᴍᴀᴀ ᴍᴀʀ ɢʏɪ ¿😆😆😆"]

# --- CORE LOGIC ---
def is_auth(uid): return uid in OWNER_IDS or uid in SUDO_USERS

async def run_loop(bot, chat_id, text, patterns, mode="title", target_id=None):
    i = 0
    while True:
        try:
            p = patterns[i % len(patterns)]
            content = p.format(text=text)
            if mode == "title": await bot.set_chat_title(chat_id, content)
            elif mode == "msg": await bot.send_message(chat_id, content)
            elif mode == "reply": await bot.send_message(chat_id, content, reply_to_message_id=target_id)
            i += 1; await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError: break
        except: await asyncio.sleep(1)

# --- SARKAR HELP BOX ---
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update.effective_user.id): return
    h = (
        "🔱 **SARKAR - MULTI BOT SYSTEM** 🔱\n\n"
        "🔥 **NC:** /hindinc, /urdunc, /bengalinc, /biharinc, /englishnc\n"
        "🚀 **SPAM:** /spam1, /spam2, /spam3, /spam4\n"
        "⚡ **OTHER:** /slid1, /slid2, /slid3, /swipe, /admin, /stopall, /bye, /phtloop\n\n"
        "🛡️ **SUDO:** /addsudo, /delsudo, /sudolist"
    )
    await update.message.reply_text(h, parse_mode="Markdown")

# --- COMMAND HANDLERS ---
async def handle_nc(update, context, patterns):
    if not is_auth(update.effective_user.id): return
    txt = " ".join(context.args) if context.args else "SARKAR"
    cid = update.effective_chat.id
    for b in bots:
        t = asyncio.create_task(run_loop(b, cid, txt, patterns))
        GLOBAL_TASKS[cid].append(t)
    await update.message.reply_text("✅ SARKAR NC STARTED!")

async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update.effective_user.id): return
    cid = update.effective_chat.id
    if cid in GLOBAL_TASKS:
        for t in GLOBAL_TASKS[cid]: t.cancel()
        GLOBAL_TASKS[cid] = []
        await update.message.reply_text("🛑 ALL SARKAR TASKS STOPPED!")

# --- BOOTSTRAP ---
def build_app(token):
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("hindinc", lambda u, c: handle_nc(u, c, HINDINC_P)))
    app.add_handler(CommandHandler("urdunc", lambda u, c: handle_nc(u, c, URDUNC_P)))
    app.add_handler(CommandHandler("bengalinc", lambda u, c: handle_nc(u, c, BENGALINC_P)))
    app.add_handler(CommandHandler("biharinc", lambda u, c: handle_nc(u, c, BIHARINC_P)))
    app.add_handler(CommandHandler("englishnc", lambda u, c: handle_nc(u, c, ENGLISHNC_P)))
    app.add_handler(CommandHandler("stopall", stopall))
    return app

async def main():
    threading.Thread(target=run_uptime_server, daemon=True).start()
    for token in TOKENS:
        try:
            a = build_app(token)
            apps.append(a); bots.append(a.bot)
            await a.initialize(); await a.start(); await a.updater.start_polling()
        except: pass
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

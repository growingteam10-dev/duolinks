import requests, os, threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler

BOT_TOKEN = os.environ.get("9164390255:AAFRGrrlIlsaaTzmAfKueF1yLzjsqU-V6j0", "").strip()
DUOLINKS_API = "f307d926c85ce7ccb657bf6e4a1a9f520951ada8"
API_URL = "https://duolinks.in/api"

app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Flipping Loots Bot is Live!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to Flipping Loots Shortner!\n\nKoi bhi link bhejo, mai turant duolinks.in ka short link bana dunga.")

def make_short(long_url):
    try:
        r = requests.get(API_URL, params={'api': DUOLINKS_API, 'url': long_url}, timeout=15)
        data = r.json()
        return data.get('shortenedUrl') or data.get('shortenedurl')
    except:
        return None

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.startswith("http"):
        await update.message.reply_text("Bhai link bhejo - https:// se shuru hone wala")
        return
    wait_msg = await update.message.reply_text("⏳ Flipping Loots se short ho raha hai...")
    short = make_short(text)
    if short:
        await wait_msg.edit_text(f"✅ Ho gaya!\n\n⚡ Short Link: {short}\n\nShare karo - Flipping Loots")
    else:
        await wait_msg.edit_text("❌ Error hai, thodi der me try karo.")

def run_bot():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    print("Flipping Loots Bot Live...")
    app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    run_bot()
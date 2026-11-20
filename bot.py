import os
import re
import threading
import requests
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Keys Render ke Environment Variables se aayengi (Safe tarika)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
DUOLINKS_API_KEY = os.environ.get("DUOLINKS_API_KEY")
DUOLINKS_API_URL = os.environ.get("DUOLINKS_API_URL", "https://duolinks.in/api")

# Render ko active rakhne ke liye chota web server
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is running 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)

def shorten_with_duolinks(long_url):
    params = {"api": DUOLINKS_API_KEY, "url": long_url}
    try:
        response = requests.get(DUOLINKS_API_URL, params=params, timeout=10)
        data = response.json()
        if data.get("status") == "success":
            return data.get("shortenedUrl")
        return f"❌ Error: {data.get('message', 'Link short nahi ho paya.')}"
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **Namaste! DuoLinks Shortener Bot mein aapka swagat hai.**\n\n"
        "Mujhe koi bhi link bhejein, main turant short link bana dunga!",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return

    urls = re.findall(r'(https?://[^\s]+)', text)
    if not urls:
        await update.message.reply_text("⚠️ Kripya koi valid link (http:// ya https://) bhejein.")
        return

    processing_msg = await update.message.reply_text("⏳ Link short kiya ja raha hai...")
    shortened_results = [f"🔗 **Short Link:**\n`{shorten_with_duolinks(u)}`" for u in urls]
    await processing_msg.edit_text("\n\n".join(shortened_results), parse_mode="Markdown")

def main():
    # Web server ko background thread mein start karein
    threading.Thread(target=run_web, daemon=True).start()

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot aur Web Server dono chal rahe hain...")
    app.run_polling()

if __name__ == "__main__":
    main()

import os
import json
import logging
import requests
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ---------------- CONFIG ----------------
BOT_TOKEN = "8406310603:AAF6eSzyj3ZJL7vBLTDTgYn0EkseWM0Vc_s"
PUBLIC_CHANNEL = -1002662162108
GROUP_ID = -1002261063910
PRIVATE_CHANNEL = -1002537631509
BACKUP_CHANNEL = -1003077556682
SHORTLINK_API = "a1cea9752ca22b304682220c274fa51e504b6e04"

logging.basicConfig(level=logging.INFO)
bot = Bot(BOT_TOKEN)

DB_FILE = "movies.json"

# --------- Load/Save JSON Database ----------
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Initial load
movie_cache = load_db()

# -------- Shortlink Generator ----------
def make_shortlink(url: str) -> str:
    try:
        api_url = f"https://shrinkme.io/api?api={SHORTLINK_API}&url={url}"
        r = requests.get(api_url).json()
        return r.get("shortenedUrl", url)
    except Exception as e:
        logging.error(f"Shortlink error: {e}")
        return url

# -------- Start Command ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Send me a movie name to search.")

# -------- Handle Movie Search ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()

    # STEP 1: Check if already in DB
    if query.lower() in movie_cache:
        movie_text = movie_cache[query.lower()]
        await update.message.reply_text("✅ Found in Database! Sending...")
        await bot.send_message(chat_id=PUBLIC_CHANNEL, text=movie_text)
        await bot.send_message(chat_id=BACKUP_CHANNEL, text=movie_text)
        return

    # STEP 2: Not Found → Generate shortlink + Save
    fake_movie_url = f"https://example.com/{query.replace(' ', '_')}"  # placeholder
    short_url = make_shortlink(fake_movie_url)

    movie_text = f"🎬 {query}\n🔗 Link: {short_url}"

    # Save in DB
    movie_cache[query.lower()] = movie_text
    save_db(movie_cache)

    # Upload to Private DB
    msg = await bot.send_message(chat_id=PRIVATE_CHANNEL, text=movie_text, parse_mode="Markdown")

    # Forward to Public + Backup
    await bot.forward_message(chat_id=PUBLIC_CHANNEL, from_chat_id=PRIVATE_CHANNEL, message_id=msg.message_id)
    await bot.forward_message(chat_id=BACKUP_CHANNEL, from_chat_id=PRIVATE_CHANNEL, message_id=msg.message_id)

    await update.message.reply_text("📤 Added to Database & Shared to Channels!")

# -------- Main Function ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()


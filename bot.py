import logging
import requests
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ---------------- CONFIG ----------------
BOT_TOKEN = "8406310603:AAE3pDq0mFnuI5xT1KLFvbcFUhr-LGwCan8"
PUBLIC_CHANNEL = -1002662162108
GROUP_ID = -1002261063910
PRIVATE_CHANNEL = -1002537631509
BACKUP_CHANNEL = -1003077556682
SHORTLINK_API = "a1cea9752ca22b304682220c274fa51e504b6e04"

logging.basicConfig(level=logging.INFO)
bot = Bot(BOT_TOKEN)

# -------- Shortlink Generator ----------
def make_shortlink(url: str) -> str:
    try:
        api_url = f"https://shrinkme.io/api?api={SHORTLINK_API}&url={url}"
        r = requests.get(api_url).json()
        return r["shortenedUrl"]
    except:
        return url

# -------- Start Command ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Send me a movie name to search.")

# -------- Handle Movie Search ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    user_id = update.message.from_user.id

    # STEP 1: Check if movie already in PRIVATE CHANNEL
    async for msg in bot.get_chat_history(PRIVATE_CHANNEL, limit=50):
        if query.lower() in (msg.text or "").lower():
            await update.message.reply_text("✅ Found in Database! Sending...")
            await bot.forward_message(chat_id=PUBLIC_CHANNEL, from_chat_id=PRIVATE_CHANNEL, message_id=msg.message_id)
            await bot.forward_message(chat_id=BACKUP_CHANNEL, from_chat_id=PRIVATE_CHANNEL, message_id=msg.message_id)
            return

    # STEP 2: Not Found → Generate shortlink + Save
    fake_movie_url = f"https://example.com/{query.replace(' ', '_')}"  # Replace with real link grabber later
    short_url = make_shortlink(fake_movie_url)

    movie_text = f"🎬 {query}\n🔗 Link: {short_url}"

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
    

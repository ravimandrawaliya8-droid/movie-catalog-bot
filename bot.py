import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 🔹 Configurations (aapke diye huye values)
BOT_TOKEN = "8406310603:AAE3pDq0mFnuI5xT1KLFvbcFUhr-LGwCan8"
PUBLIC_CHANNEL_ID = -1003077556682       # First public channel id
GROUP_ID = -1002261063910               # Second group id
PRIVATE_CHANNEL_ID = -1002537631509     # Third private channel id
BACKUP_CHANNEL_ID = -1002662162108      # Backup channel id
SHORTENER_API = "a1cea9752ca22b304682220c274fa51e504b6e04"  # ShrinkMe API key
SHORTENER_URL = "https://shrinkme.io/api"

# 🔹 Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔹 Function: Shorten URL
def shorten_url(long_url: str) -> str:
    try:
        params = {"api": SHORTENER_API, "url": long_url}
        res = requests.get(SHORTENER_URL, params=params).json()
        if res.get("status") == "success":
            return res["shortenedUrl"]
        else:
            return long_url
    except Exception as e:
        logger.error(f"Shortener error: {e}")
        return long_url

# 🔹 Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is running! Send me any link and I’ll auto-upload with shortlink.")

# 🔹 Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text.startswith("http"):
        short_url = shorten_url(text)

        msg = f"🎬 New Movie Uploaded!\n\n👉 {short_url}"

        # Send to channels and groups
        await context.bot.send_message(chat_id=PUBLIC_CHANNEL_ID, text=msg)
        await context.bot.send_message(chat_id=PRIVATE_CHANNEL_ID, text=msg)
        await context.bot.send_message(chat_id=BACKUP_CHANNEL_ID, text=msg)
        await context.bot.send_message(chat_id=GROUP_ID, text=msg)

        await update.message.reply_text(f"✅ Uploaded Successfully!\n\n🔗 {short_url}")
    else:
        await update.message.reply_text("⚠️ Please send a valid movie link (http/https).")

# 🔹 Main function
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()

import os
import json
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load environment variables (optional but secure)
BOT_TOKEN = os.environ.get("BOT_TOKEN") or "7538168447:AAF7SLFoJQdXv7C5vv2Wjhk9_petWTnzaT0"
SHORTENER_API = os.environ.get("SHORTENER_API") or "ebf67289ffbeb073bf5d0dd8a3c4b6d01fc16c71"
SHORTENER_URL = "https://shrinkme.io/api"

# Load movie links
with open("movies.json", "r") as f:
    movie_data = json.load(f)

# === /start command ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "👋 Welcome to *SnapMovies*!\n\n"
        "🎬 Send /movie <name> to get the download link.\n"
        "💸 All links are monetized to support us. Thanks!"
    )
    await update.message.reply_text(welcome, parse_mode='Markdown')

# === /movie command ===
async def movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Please provide a movie name. Example:\n`/movie avengers`", parse_mode='Markdown')
        return

    query = " ".join(context.args).lower()

    if query not in movie_data:
        await update.message.reply_text("❌ Movie not found in my database.")
        return

    original_url = movie_data[query]

    try:
        res = requests.get(
            f"{SHORTENER_URL}?api={SHORTENER_API}&url={original_url}"
        ).json()

        if res["status"] == "success":
            short_url = res["shortenedUrl"]
            btn = InlineKeyboardMarkup([
                [InlineKeyboardButton("📥 Download Movie", url=short_url)]
            ])
            await update.message.reply_text(f"🎬 *{query.title()}* download ready:", reply_markup=btn, parse_mode='Markdown')
        else:
            await update.message.reply_text("⚠️ Failed to shorten the URL.")
    except Exception as e:
        await update.message.reply_text(f"🚫 Error: {e}")

# === Main ===
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("movie", movie))
    app.run_polling()

if __name__ == "__main__":
    main()
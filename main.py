import os
import json
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Your bot and GPLinks credentials
BOT_TOKEN = "7538168447:AAF7SLFoJQdXv7C5vv2Wjhk9_petWTnzaT0"
GPLINKS_API = "ebf67289ffbeb073bf5d0dd8a3c4b6d01fc16c71"

# Load movie links from a JSON file
with open("movies.json", "r") as f:
    movie_data = json.load(f)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "🎬 *Welcome to SnapMovies Bot!*\n\n"
        "Send `/movie <name>` to get the download link.\n"
        "Thanks for supporting us ❤️"
    )
    await update.message.reply_text(message, parse_mode='Markdown')

# /movie command
async def movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Use like this: `/movie joker`", parse_mode='Markdown')
        return

    movie_name = " ".join(context.args).lower()
    original_url = movie_data.get(movie_name)

    if not original_url:
        await update.message.reply_text("❌ Movie not found. Ask admin to add it.")
        return

    # Shorten using GPLinks
    try:
        api_url = f"https://gplinks.in/api?api={GPLINKS_API}&url={original_url}"
        response = requests.get(api_url).json()
        if response.get("status") == "success":
            short_url = response["shortenedUrl"]
        else:
            short_url = original_url
    except:
        short_url = original_url

    button = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📥 Download Link", url=short_url)]]
    )

    await update.message.reply_text(
        f"🎬 *{movie_name.title()}* is ready to download:",
        reply_markup=button,
        parse_mode='Markdown'
    )

# Start bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("movie", movie))
    app.run_polling()

if __name__ == "__main__":
    main()
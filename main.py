import os
import json
import requests
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GPLINKS_API = os.getenv("GPLINKS_API")

# Flask server for keep-alive
app = Flask('')

@app.route('/')
def home():
    return "✅ SnapMovies Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Load movie data
try:
    with open("movies.json", "r") as f:
        movie_data = json.load(f)
except FileNotFoundError:
    movie_data = {}
    print("⚠️ 'movies.json' not found!")

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
        short_url = response.get("shortenedUrl", original_url)
    except Exception as e:
        print(f"Shorten error: {e}")
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
    keep_alive()  # to prevent bot from sleeping
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("movie", movie))
    app.run_polling()

if __name__ == "__main__":
    main()
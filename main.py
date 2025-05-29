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
ADMIN_ID = 7517451776  # ✅ Your Telegram user ID

# Flask server to keep bot alive (for Railway, etc.)
app = Flask('')

@app.route('/')
def home():
    return "✅ SnapMovies Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "🎬 *Welcome to SnapMovies Bot!*\n\n"
        "Send `/movie <name>` to get the download link.\n"
        "Thanks for supporting us ❤️"
    )
    await update.message.reply_text(message, parse_mode='Markdown')

# /movie command (partial + case-insensitive matching)
async def movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Use like this: `/movie joker`", parse_mode='Markdown')
        return

    search_query = " ".join(context.args).lower()

    # Reload movie data
    try:
        with open("movies.json", "r") as f:
            movie_data = json.load(f)
    except FileNotFoundError:
        movie_data = {}

    matched_movie = None
    for title, url in movie_data.items():
        if search_query in title.lower():
            matched_movie = (title, url)
            break

    if not matched_movie:
        await update.message.reply_text("❌ Movie not found. Ask admin to add it.")
        return

    movie_title, original_url = matched_movie

    # Shorten URL
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
        f"🎬 *{movie_title.title()}* is ready to download:",
        reply_markup=button,
        parse_mode='Markdown'
    )

# /addmovie command (admin-only)
async def add_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ You are not allowed to use this command.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("❗ Use like this:\n`/addmovie joker https://link.com`", parse_mode='Markdown')
        return

    name = " ".join(context.args[:-1]).lower()
    url = context.args[-1]

    try:
        try:
            with open("movies.json", "r") as f:
                movie_data = json.load(f)
        except FileNotFoundError:
            movie_data = {}

        movie_data[name] = url
        with open("movies.json", "w") as f:
            json.dump(movie_data, f, indent=2)

        await update.message.reply_text(f"✅ *{name.title()}* added successfully!", parse_mode='Markdown')
    except Exception as e:
        print(f"AddMovie Error: {e}")
        await update.message.reply_text("❌ Failed to add movie.")

# Start bot
def main():
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("movie", movie))
    app.add_handler(CommandHandler("addmovie", add_movie))
    app.run_polling()

if __name__ == "__main__":
    main()
import json
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# === BOT SETTINGS ===
BOT_TOKEN = "7538168447:AAF7SLFoJQdXv7C5vv2Wjhk9_petWTnzaT0"
SHORTENER_API = "ebf67289ffbeb073bf5d0dd8a3c4b6d01fc16c71"
SHORTENER_URL = "https://shrinkme.io/api"

# === LOAD MOVIES LIST ===
def load_movies():
    with open("movies.json", "r") as f:
        return json.load(f)

# === SHORTEN LINK FUNCTION ===
def shorten_url(original_url):
    params = {
        "api": SHORTENER_API,
        "url": original_url
    }
    res = requests.get(SHORTENER_URL, params=params)
    data = res.json()
    return data.get("shortenedUrl", original_url)

# === /start COMMAND ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to SnapMovies Bot!\nUse /movie <name> to search movies.")

# === /movie COMMAND ===
async def movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Please provide a movie name.\nExample: /movie avengers")
        return

    query = " ".join(context.args).lower()
    movies = load_movies()

    if query in movies:
        original_url = movies[query]
        short_url = shorten_url(original_url)

        keyboard = [[InlineKeyboardButton("📥 Download", url=short_url)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"🎬 *{query.title()}*\n\nHere's your download link:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ Movie not found. Please try another name.")

# === MAIN ===
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("movie", movie))
app.run_polling()
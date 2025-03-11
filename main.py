import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup
from config import BOT_TOKEN, API_ID, API_HASH, CHANNEL_ID, OWNER_ID
from database import add_file, get_random_file, get_total_files, delete_all_files
from fastapi import FastAPI
import uvicorn
import threading

# Enable Logging
logging.basicConfig(level=logging.INFO)

# Convert OWNER_ID to int if it's a string
try:
    OWNER_ID = int(OWNER_ID)
except ValueError:
    logging.error("OWNER_ID must be an integer!")
    exit()

# Initialize bot
bot = Client("BotSession", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# FastAPI Health Check
app = FastAPI()

@app.get("/")
async def home():
    return {"status": "running"}

def run_web_server():
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")

threading.Thread(target=run_web_server, daemon=True).start()

# Reply Keyboard
keyboard = ReplyKeyboardMarkup([["📁 Content"]], resize_keyboard=True)

@bot.on_message(filters.command("start"))
async def start(bot, message):
    await message.reply_text("Welcome! Click '📁 Content' to get a random file.", reply_markup=keyboard)

@bot.on_message(filters.text & filters.regex("📁 Content"))
async def send_random_file(bot, message):
    file_id = await get_random_file()
    if file_id:
        await bot.send_document(message.chat.id, file_id)
    else:
        await message.reply_text("No files available. Please wait for indexing.")

@bot.on_message(filters.command("index"))
async def index_files(bot, message):
    if message.from_user.id != OWNER_ID:
        await message.reply_text("❌ You are not authorized to use this command.")
        return

    try:
        async for msg in bot.search_messages(CHANNEL_ID, limit=1000):
            if msg.document or msg.video or msg.photo:
                file_id = msg.document.file_id if msg.document else msg.video.file_id if msg.video else msg.photo.file_id
                await add_file(file_id)
        await message.reply_text("✅ Indexing complete.")
    except Exception as e:
        logging.error(f"Error in /index: {e}")
        await message.reply_text(f"❌ Error: {e}")

@bot.on_message(filters.command("status"))
async def status(bot, message):
    if message.from_user.id != OWNER_ID:
        await message.reply_text("❌ You are not authorized to use this command.")
        return

    try:
        total = await get_total_files()
        await message.reply_text(f"📊 Total files indexed: {total}")
    except Exception as e:
        logging.error(f"Error in /status: {e}")
        await message.reply_text(f"❌ Error: {e}")

@bot.on_message(filters.command("delete_all"))
async def delete_all(bot, message):
    if message.from_user.id != OWNER_ID:
        await message.reply_text("❌ You are not authorized to use this command.")
        return

    try:
        await delete_all_files()
        await message.reply_text("🗑️ All indexed files have been deleted.")
    except Exception as e:
        logging.error(f"Error in /delete_all: {e}")
        await message.reply_text(f"❌ Error: {e}")

bot.run()

import asyncio
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup
from config import BOT_TOKEN, API_ID, API_HASH, CHANNEL_ID, OWNER_ID
from database import add_file, get_random_file, get_total_files, delete_all_files

bot = Client("BotSession", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

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

@bot.on_message(filters.command("index") & filters.user(OWNER_ID))
async def index_files(bot, message):
    indexed = 0
    async for msg in bot.get_chat_history(CHANNEL_ID, limit=1000):
        if msg.document or msg.video or msg.photo:
            await add_file(msg.document.file_id if msg.document else msg.video.file_id if msg.video else msg.photo.file_id)
            indexed += 1
    await message.reply_text(f"Indexed {indexed} files.")

@bot.on_message(filters.command("status") & filters.user(OWNER_ID))
async def status(bot, message):
    total = await get_total_files()
    await message.reply_text(f"Total files indexed: {total}")

@bot.on_message(filters.command("delete_all") & filters.user(OWNER_ID))
async def delete_all(bot, message):
    await delete_all_files()
    await message.reply_text("All indexed files have been deleted.")

bot.run()

import random
import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid, BotMethodInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from config import API_ID, API_HASH, BOT_TOKEN, MONGO_URL, DATABASE_NAME, CHANNEL_ID, FSUB_CHANNEL, AUTO_DELETE_TIME, OWNER_ID

# Initialize bot & database
bot = Client("video_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
mongo = MongoClient(MONGO_URL)
db = mongo[DATABASE_NAME]
collection = db["videos"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to check force subscription
async def check_fsub(client, user_id):
    try:
        chat_member = await client.get_chat_member(FSUB_CHANNEL, user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# Function to fetch and send a random video
async def send_random_video(client, chat_id):
    video_docs = list(collection.find())
    if not video_docs:
        await client.send_message(chat_id, "⚠ No videos available. Use /index first!")
        return

    random_video = random.choice(video_docs)
    sent_msg = await client.forward_messages(chat_id=chat_id, from_chat_id=CHANNEL_ID, message_ids=random_video["message_id"])

    if AUTO_DELETE_TIME > 0:
        await asyncio.sleep(AUTO_DELETE_TIME)
        await sent_msg.delete()

# Command to manually index videos
@bot.on_message(filters.command("index") & filters.user(OWNER_ID))
async def index_videos(client, message):
    await message.reply_text("🔄 Indexing videos... This may take a while.")

    indexed_count = 0
    try:
        async for msg in client.get_chat_history(CHANNEL_ID, limit=1000):
            if msg.video:
                collection.update_one(
                    {"message_id": msg.message_id},
                    {"$set": {"message_id": msg.message_id}},
                    upsert=True
                )
                indexed_count += 1
    except (PeerIdInvalid, BotMethodInvalid) as e:
        logger.error(f"Indexing error: {e}")
        await message.reply_text("❌ Indexing failed. Make sure the bot is **admin** in the channel!")

    await message.reply_text(f"✅ Indexing completed! {indexed_count} videos added.")

# Start command with inline button
@bot.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id

    if not await check_fsub(client, user_id):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FSUB_CHANNEL}")]
        ])
        await message.reply_text("🚨 You must join our channel to use this bot!", reply_markup=keyboard)
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎥 Get Random Video", callback_data="get_random_video")],
        [InlineKeyboardButton("🔄 Index Videos (Admin Only)", callback_data="index_videos")]
    ])
    await message.reply_text("✅ Welcome! Use the buttons below:", reply_markup=keyboard)

# Callback for random video
@bot.on_callback_query(filters.regex("get_random_video"))
async def random_video_callback(client, callback_query):
    await send_random_video(client, callback_query.message.chat.id)
    await callback_query.answer()

# Callback for indexing videos (Only Owner)
@bot.on_callback_query(filters.regex("index_videos"))
async def index_videos_callback(client, callback_query):
    if callback_query.from_user.id != OWNER_ID:
        await callback_query.answer("🚫 Only the owner can index videos!", show_alert=True)
        return

    await index_videos(client, callback_query.message)
    await callback_query.answer()

if __name__ == "__main__":
    bot.run()

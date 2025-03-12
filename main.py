import os
import threading
import datetime
import time
import pymongo
from flask import Flask
from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid, RPCError
from config import API_ID, API_HASH, BOT_TOKEN, MONGO_URL, DATABASE_NAME, CHANNEL_ID, FSUB_CHANNEL, AUTO_DELETE_TIME, OWNER_ID

# Flask Health Check (Fixes TCP Health Check Failure on Koyeb)
app = Flask(__name__)

@app.route("/")
def health_check():
    return "Bot is running!", 200  # Required for Koyeb health check

def run_flask():
    app.run(host="0.0.0.0", port=8080)  # Ensure Flask listens on port 8080

threading.Thread(target=run_flask, daemon=True).start()  # Run Flask in a separate thread

# Initialize Telegram Bot
bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Connect to MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client[DATABASE_NAME]
videos_col = db["videos"]
users_col = db["users"]

# Check if user is subscribed (Force Subscribe)
async def is_user_subscribed(user_id):
    if not FSUB_CHANNEL:
        return True  # Skip check if no channel set
    try:
        member = await bot.get_chat_member(FSUB_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except RPCError:
        return False  # Assume not subscribed

# /start Command
@bot.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.chat.id

    if FSUB_CHANNEL and not await is_user_subscribed(user_id):
        await message.reply_text(
            f"🚨 You must join our channel to use this bot!\n\n🔗 [Join Here](https://t.me/{FSUB_CHANNEL})",
            disable_web_page_preview=True
        )
        return
    
    await message.reply_text("✅ Welcome! Use /random to get a random video.")

# /index Command (Owner Only) - Now Supports 1K+ Videos
@bot.on_message(filters.command("index") & filters.user(OWNER_ID))
async def index_channel(client, message):
    try:
        chat = await client.get_chat(CHANNEL_ID)
        count = 0
        last_message_id = 0  # Start from the latest message

        while True:  # Keep fetching messages until all videos are indexed
            messages = await client.get_chat_history(chat_id=chat.id, limit=100, offset_id=last_message_id)

            if not messages:  # Stop if no more messages
                break

            for msg in messages:
                if msg.video and not videos_col.find_one({"file_id": msg.video.file_id}):
                    videos_col.insert_one({
                        "file_id": msg.video.file_id,
                        "title": msg.caption or "Untitled Video",
                        "date_added": datetime.datetime.utcnow()
                    })
                    count += 1

                last_message_id = msg.message_id  # Update last message ID for pagination

        await message.reply_text(f"✅ Indexed {count} new videos!")

    except PeerIdInvalid:
        await message.reply_text("❌ Error: Bot has not interacted with the channel. Forward a message from the channel to the bot first!")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

# /random Command (Get Random Video)
@bot.on_message(filters.command("random"))
async def send_random_video(client, message):
    user_id = message.chat.id

    if FSUB_CHANNEL and not await is_user_subscribed(user_id):
        await message.reply_text(
            f"🚨 You must join our channel to use this bot!\n\n🔗 [Join Here](https://t.me/{FSUB_CHANNEL})",
            disable_web_page_preview=True
        )
        return

    video = videos_col.aggregate([{"$sample": {"size": 1}}]).next()
    
    if video:
        sent_message = await message.reply_video(video=video["file_id"], caption=video["title"])
        
        if AUTO_DELETE_TIME > 0:
            await bot.delete_messages(
                chat_id=message.chat.id, 
                message_ids=[sent_message.message_id], 
                revoke=True, 
                schedule_date=int(time.time()) + AUTO_DELETE_TIME
            )
    else:
        await message.reply_text("⚠ No videos found. Use /index to add videos.")

# Start Bot
if __name__ == "__main__":
    bot.run()

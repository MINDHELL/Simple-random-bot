import os

API_ID = int(os.getenv("API_ID", "27788368"))  # Replace with your API ID
API_HASH = os.getenv("API_HASH", "9df7e9ef3d7e4145270045e5e43e1081")  # Replace with your API Hash
BOT_TOKEN = os.getenv("BOT_TOKEN", "7888029778:AAHeC7P5zONGjN3mY5q0Rm6-V1zzPx1ywEQ")  # Replace with your Bot Token

MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://aarshhub:6L1PAPikOnAIHIRA@cluster0.6shiu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # MongoDB connection string
DATABASE_NAME = os.getenv("DATABASE_NAME", "Hd_content")  # MongoDB database name

CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1002242458059"))  # Channel where videos are indexed
FSUB_CHANNEL = os.getenv("FSUB_CHANNEL", "test89p")  # Force subscription channel

AUTO_DELETE_TIME = int(os.getenv("AUTO_DELETE_TIME", "10"))  # Auto-delete sent videos (seconds)
OWNER_ID = int(os.getenv("OWNER_ID", "6860316927"))  # Replace with your Telegram user ID

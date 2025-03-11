from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL

client = AsyncIOMotorClient(MONGO_URL)
db = client["TelegramBot"]
files_col = db["files"]

async def add_file(file_id):
    await files_col.insert_one({"file_id": file_id})

async def get_random_file():
    file = await files_col.aggregate([{ "$sample": { "size": 1 } }]).to_list(1)
    return file[0]["file_id"] if file else None

async def get_total_files():
    return await files_col.count_documents({})

async def delete_all_files():
    await files_col.delete_many({})

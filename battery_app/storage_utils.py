# storage_utils.py
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from gridfs import GridFS

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

if not MONGO_URI or not MONGO_DB:
    raise RuntimeError("❌ MONGO_URI or MONGO_DB not set in environment variables")

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
fs = GridFS(db)

# Hugging Face–safe cache directory
CACHE_DIR = "/data/cached_files"
os.makedirs(CACHE_DIR, exist_ok=True)


def get_file_from_gridfs(filename: str) -> str:
    """
    Fetch file from GridFS and cache it locally.
    Returns local file path.
    """
    local_path = os.path.join(CACHE_DIR, filename)

    # Use cached file if exists
    if os.path.exists(local_path):
        print(f"✅ Using cached file: {filename}")
        return local_path

    # Fetch from GridFS
    file_obj = fs.find_one({"filename": filename})
    if not file_obj:
        raise FileNotFoundError(f"❌ {filename} not found in GridFS")

    with open(local_path, "wb") as f:
        f.write(file_obj.read())

    print(f"📥 Downloaded from GridFS: {filename}")
    return local_path

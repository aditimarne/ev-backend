# storage_utils.py
import os

from dotenv import load_dotenv
from gridfs import GridFS
from pymongo import MongoClient

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB")]
fs = GridFS(db)

CACHE_DIR = "./cached_files"
os.makedirs(CACHE_DIR, exist_ok=True)

def get_file_from_gridfs(filename):
    local_path = os.path.join(CACHE_DIR, filename)

    # Check local cache
    if os.path.exists(local_path):
        print(f"✅ Using cached: {filename}")
        return local_path

    # Fetch from GridFS
    file_obj = fs.find_one({"filename": filename})
    if not file_obj:
        raise FileNotFoundError(f"{filename} not found in GridFS")

    with open(local_path, "wb") as f:
        f.write(file_obj.read())

    print(f"📥 Downloaded from GridFS: {filename}")
    return local_path
    return local_path

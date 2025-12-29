from pymongo import MongoClient
from gridfs import GridFS
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB")]
fs = GridFS(db)

FILES = [
    "DNEW2.csv",
    "soh2_xgboost_model.json",
    "rul2_lstm_model.h5",
    "RV4.csv",
    "soh1_model.json",
    "rul1_model.h5"
]

for file in FILES:
    if not os.path.exists(file):
        print(f"❌ File not found locally: {file}")
        continue

    if fs.find_one({"filename": file}):
        print(f"✅ Already exists in GridFS: {file}")
        continue

    with open(file, "rb") as f:
        fs.put(f, filename=file)
        print(f"📤 Uploaded: {file}")

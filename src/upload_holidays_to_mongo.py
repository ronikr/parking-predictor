from pymongo import MongoClient
import json
import os
from dotenv import load_dotenv

load_dotenv()

def upload_to_mongo(flattened_data, mongo_uri, db_name="parking_app", collection_name="hourly_predictions_holiday"):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    if flattened_data:
        collection.insert_many(flattened_data)
        print(f"✅ Inserted {len(flattened_data)} records into {db_name}.{collection_name}")
    else:
        print("⚠️ No data to insert.")


# Example usage
if __name__ == "__main__":
    file_path = "../data/output/hourly_predictions_holiday.json"

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ File not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI is not set in environment variables.")

    upload_to_mongo(data, mongo_uri)

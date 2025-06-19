from pymongo import MongoClient
import json
import os
from dotenv import load_dotenv

load_dotenv()


def upload_to_mongo(flattened_data, mongo_uri, db_name="parking_app", collection_name="hourly_predictions", wipe=False):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    if wipe:
        collection.delete_many({})  # 💣 Wipe existing data
        print(f"🗑 Cleared collection {collection_name}")

    if flattened_data:
        collection.insert_many(flattened_data)
        print(f"✅ Inserted {len(flattened_data)} records into {db_name}.{collection_name}")
    else:
        print("⚠️ No data to insert.")


# Example usage
if __name__ == "__main__":
    file_regular = "../data/output/hourly_predictions.json"
    file_holiday = "../data/output/hourly_predictions_holiday.json"

    if not os.path.exists(file_regular):
        raise FileNotFoundError(f"❌ File not found: {file_regular}")
    if not os.path.exists(file_holiday):
        raise FileNotFoundError(f"❌ File not found: {file_holiday}")

    with open(file_regular, "r", encoding="utf-8") as f:
        regular_data = json.load(f)

    with open(file_holiday, "r", encoding="utf-8") as f:
        holiday_data = json.load(f)

    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI is not set in environment variables.")

    print("🧼 Wiping and uploading regular data...")
    upload_to_mongo(regular_data, mongo_uri, wipe=True)
# both weekdays and holiday are added to the same db, don't use wipe in the second!
    print("➕ Adding holiday data on top...")
    upload_to_mongo(holiday_data, mongo_uri, wipe=False)



from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise ValueError("MONGO_URI is not set in environment variables.")

client = MongoClient(mongo_uri)
db = client["parking_app"]
collection = db["hourly_predictions"]

# Example Query: All lots with availability data for Monday at 17:00
query = {
    "weekday": "monday",
    "hour": 17,
    "prediction.available": {"$gt": 0.0}  # optional filter
}

projection = {
    "_id": 0,
    "lot_id": 1,
    "name": 1,
    "prediction": 1,
    "url": 1
}

results = list(collection.find(query, projection).limit(3))

print("\nExample query: Monday at 17:00")
for item in results:
    pprint(item)

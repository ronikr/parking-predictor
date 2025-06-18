from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://127.0.0.1:5500"] during dev
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise ValueError("MONGO_URI is not set in environment variables.")

client = MongoClient(mongo_uri)
db = client["parking_app"]
hourly_predictions = db["hourly_predictions"]
lots_static = db["lots_static"]


@app.get("/lots")
def get_lots():
    lots = list(lots_static.find({}, {"_id": 0}))
    return lots


@app.get("/prediction")
def get_prediction(lot_id: str = Query(...), weekday: str = Query(...), hour: int = Query(...)):
    query = {"lot_id": lot_id, "weekday": weekday, "hour": hour}
    result = hourly_predictions.find_one(query, {"_id": 0, "lot_id": 1, "weekday": 1, "hour": 1, "prediction": 1, "url": 1})

    if not result:
        raise HTTPException(status_code=404, detail="Prediction not found")

    return result


@app.get("/availability")
def get_availability(weekday: str = Query(...), hour: int = Query(...)):
    query = {"weekday": weekday, "hour": hour}
    projection = {"_id": 0, "lot_id": 1, "name": 1, "location": 1, "prediction": 1}

    results = list(hourly_predictions.find(query, projection))

    for item in results:
        lot_prediction = item.get("prediction", {})

        max_prob = -1
        max_status = "no_data"

        for status, prob in lot_prediction.items():
            if prob > max_prob:
                max_prob = prob
                max_status = status

        item["status"] = max_status

    return results

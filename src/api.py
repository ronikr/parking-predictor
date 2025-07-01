from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from dotenv import load_dotenv
from pydantic import BaseModel
from datetime import datetime, timezone
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import pytz
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

# Create limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://parking-predictor-ui.onrender.com",  # Your frontend domain
        # "http://localhost:3000",                      # Local development
        # "http://127.0.0.1:8000",                     # Local testing
        # "http://localhost:8000",                      # Alternative local
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],  # Only the methods you actually use
    allow_headers=["*"],
)

mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise ValueError("MONGO_URI is not set in environment variables.")

client = MongoClient(mongo_uri)
db = client["parking_app"]
hourly_predictions = db["hourly_predictions"]
lots_static = db["lots_static"]
realtime_lots = db["realtime_lots"]  # NEW: Realtime collection


class LotUpdate(BaseModel):
    id: str
    name: str
    status: str
    timestamp: str


@app.get("/lots")
@limiter.limit("60/minute")  # Used by both maps
def get_lots(request: Request):
    lots = list(lots_static.find({}, {"_id": 0}))
    return lots


@app.get("/prediction")
@limiter.limit("30/minute")  # Planning users - less frequent
def get_prediction(request: Request, lot_id: str = Query(...), weekday: str = Query(...), hour: int = Query(...)):
    query = {"lot_id": lot_id, "weekday": weekday, "hour": hour}
    result = hourly_predictions.find_one(query,
                                         {"_id": 0, "lot_id": 1, "weekday": 1, "hour": 1, "prediction": 1, "url": 1})

    if not result:
        raise HTTPException(status_code=404, detail="Prediction not found")

    return result


@app.get("/availability")
@limiter.limit("30/minute")  # Planning users - less frequent
def get_availability(request: Request, weekday: str = Query(...), hour: int = Query(...)):
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


# NEW REALTIME ENDPOINTS
@app.post("/update-lot")
@limiter.limit("200/minute")  # Apify only
def update_lot(request: Request, lot_data: LotUpdate):
    """Receive realtime parking data from Apify scraper"""
    try:
        # Generate timestamp when API receives the data
        israel_tz = pytz.timezone('Asia/Jerusalem')
        scrape_time = datetime.now(israel_tz).isoformat()

        lot_record = {
            'id': lot_data.id,
            'name': lot_data.name,
            'status': lot_data.status,
            'scraped_at': scrape_time  # API timestamp, not Apify timestamp
        }

        result = realtime_lots.update_one(
            {"id": lot_data.id},
            {"$set": lot_record},
            upsert=True
        )

        logger.info(f"📊 Updated lot {lot_data.id}: {lot_data.name} - {lot_data.status}")
        return {'success': True}

    except Exception as e:
        logger.error(f"❌ Error updating lot data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/lots-realtime")
@limiter.limit("60/minute")  # Realtime users
def get_realtime_lots(request: Request):
    """Get current realtime parking data for frontend map"""
    try:
        lots_cursor = realtime_lots.find({})
        lots_list = []
        scrape_timestamp = None

        for lot in lots_cursor:
            lot_data = {
                'id': lot['id'],
                'name': lot['name'],
                'status': lot['status']
            }
            lots_list.append(lot_data)

            # Get timestamp from first lot
            if scrape_timestamp is None and 'scraped_at' in lot:
                scrape_timestamp = lot['scraped_at']

        return {
            'timestamp': scrape_timestamp or "",
            'lots': lots_list
        }

    except Exception as e:
        logger.error(f"❌ Error fetching realtime lots: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


from dateutil import parser
import pytz
import csv
from datetime import datetime, timedelta

PARKING_DATA_FILE = "../data/merged_parking_data.csv"
STATIC_LOT_DATA = "../data/apify/dataset_parking-address-data.csv"


def load_static_data() -> dict:
    # organize static csv lot data into dict
    lots = {}

    with open(STATIC_LOT_DATA, encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)

        for row in reader:
            lot_id = row['lot_id']
            lots[lot_id] = {
                'address': row['address'],
                'name': row['name'],
                'url': row['url'],
                'availability': {}  # previously 'records'
            }
    return lots


def convert_utc_to_israel_time(utc_timestamp: str) -> datetime:
    dt_utc = parser.isoparse(utc_timestamp).replace(tzinfo=pytz.UTC)
    dt_il = dt_utc.astimezone(pytz.timezone("Asia/Jerusalem"))
    return dt_il  # ✅ return the datetime, not string


def insert_availability(lots_by_id: dict, lot_id: str, israel_time: datetime, availability_status: str) -> None:
    """Adds an availability status to the correct time slot in a lot's availability data."""
    weekday = israel_time.strftime('%A').lower()
    hour = israel_time.hour

    lot_data = lots_by_id[lot_id]
    availability = lot_data['availability']

    if weekday not in availability:
        availability[weekday] = {}

    if hour not in availability[weekday]:
        availability[weekday][hour] = {
            'raw': [],
            'prediction': None
        }

    availability[weekday][hour]['raw'].append(availability_status)


def map_icon_to_status(icon: str) -> str:
    mapping = {
        'panui': 'available',
        'male': 'full',
        'meat': 'limited',
        'pail': 'unknown',
        '': 'no_data'
    }
    if icon in mapping:
        return mapping[icon]
    else:
        return 'no_data'


def load_dynamic_data(lots_by_id: dict) -> dict:
    """Reads dynamic parking data from CSV and populates each lot's availability."""
    with open(PARKING_DATA_FILE, encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)

        for row in reader:
            if not row.get('id'):  # skip rows without a lot_id (summary row, etc.)
                continue

            lot_id = row['id']
            availability_status = map_icon_to_status(row['icon'])
            timestamp = row['timestamp']

            if lot_id not in lots_by_id:
                continue  # skip rows for lots not found in static data

            israel_time = convert_utc_to_israel_time(timestamp)
            insert_availability(lots_by_id, lot_id, israel_time, availability_status)

    return lots_by_id


def calculate_availability_prediction(availability_list: list) -> dict:
    availability_options = {
        'available': 0,
        'full': 0,
        'limited': 0,
        'unknown': 0,
        'no_data': 0
    }
    if not availability_list:
        availability_options['no_data'] = 1.0
        return availability_options

    for item in availability_list:
        if item in availability_options:
            availability_options[item] += 1
        else:
            availability_options['no_data'] += 1

    total = len(availability_list)

    for status in availability_options:
        availability_options[status] = round(availability_options[status] / total, 2)

    return availability_options


def add_prediction_to_lots(lots_by_id: dict) -> dict:
    for lot in lots_by_id.values():
        for day in lot['availability'].values():
            for hour in day.values():
                raw_hourly_data = hour['raw']
                lot_prediction = calculate_availability_prediction(raw_hourly_data)
                hour['prediction'] = lot_prediction
    return lots_by_id


import json
import os

def flatten_predictions(lots_by_id: dict) -> list[dict]:
    flattened = []
    for lot_id, lot_data in lots_by_id.items():
        name = lot_data.get("name")
        address = lot_data.get("address")
        url = lot_data.get("url")
        availability = lot_data.get("availability", {})

        for weekday, hours in availability.items():
            for hour, hour_data in hours.items():
                flattened.append({
                    "lot_id": lot_id,
                    "weekday": weekday,
                    "hour": hour,
                    "raw": hour_data.get("raw", []),
                    "prediction": hour_data.get("prediction", {}),
                    "name": name,
                    "address": address,
                    "url": url,
                    "location": {
                        "type": "Point",
                        "coordinates": [0.0, 0.0]  # Placeholder to be updated later
                    }
                })
    return flattened


def save_flattened_to_json(flat_data: list[dict], output_path="../data/output/hourly_predictions.json"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(flat_data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    static_lots = load_static_data()
    populated_lots = load_dynamic_data(static_lots)
    enriched_lots = add_prediction_to_lots(populated_lots)
    flat = flatten_predictions(enriched_lots)
    save_flattened_to_json(flat)
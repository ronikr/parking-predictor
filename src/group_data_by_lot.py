from dateutil import parser
import pytz
import csv
from datetime import datetime, timedelta
import json
import os

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
                'location': {
                    'type': 'Point',
                    'coordinates': [0.0, 0.0]  # Placeholder
                },
                'availability': {}
            }
    return lots


def convert_utc_to_israel_time(utc_timestamp: str) -> datetime:
    dt_utc = parser.isoparse(utc_timestamp).replace(tzinfo=pytz.UTC)
    dt_il = dt_utc.astimezone(pytz.timezone("Asia/Jerusalem"))
    return dt_il


def insert_availability(lots_by_id: dict, lot_id: str, israel_time: datetime, availability_status: str) -> None:
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
    return mapping.get(icon, 'no_data')


def load_dynamic_data(lot_dict: dict) -> None:
    with open(PARKING_DATA_FILE, encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)

        for row in reader:
            if not row.get('id'):
                continue

            lot_id = row['id']
            availability_status = map_icon_to_status(row['icon'])
            timestamp = row['timestamp']

            if lot_id not in lot_dict:
                continue

            israel_time = convert_utc_to_israel_time(timestamp)
            insert_availability(lot_dict, lot_id, israel_time, availability_status)


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


def add_prediction_to_lots(lot_dict: dict) -> None:
    for lot in lot_dict.values():
        for day in lot['availability'].values():
            for hour in day.values():
                raw_hourly_data = hour['raw']
                lot_prediction = calculate_availability_prediction(raw_hourly_data)
                hour['prediction'] = lot_prediction


def flatten_predictions(lot_dict: dict) -> list[dict]:
    flattened = []
    for lot_id, lot_data in lot_dict.items():
        name = lot_data.get("name")
        address = lot_data.get("address")
        url = lot_data.get("url")
        location = lot_data.get("location")
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
                    "location": location
                })
    return flattened


def flatten_static_metadata(lots_by_id: dict) -> list[dict]:
    return [
        {
            "lot_id": lot_id,
            "name": lot["name"],
            "address": lot["address"],
            "url": lot["url"],
            "location": lot.get("location", {"type": "Point", "coordinates": [0.0, 0.0]})
        }
        for lot_id, lot in lots_by_id.items()
    ]


def save_flattened_availabilities_to_json(flat_data: list[dict], output_path="../data/output/hourly_predictions.json"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(flat_data, f, indent=2, ensure_ascii=False)


def save_flattened_static_to_json(static_data: list[dict], output_path="../data/output/lots_static.json"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(static_data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    lot_data = load_static_data()
    flat_static = flatten_static_metadata(lot_data)
    save_flattened_static_to_json(flat_static)

    load_dynamic_data(lot_data)
    add_prediction_to_lots(lot_data)
    flat_predictions = flatten_predictions(lot_data)
    save_flattened_availabilities_to_json(flat_predictions)

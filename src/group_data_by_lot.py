from dateutil import parser
import pytz
import csv
from datetime import datetime, timedelta
import json
import os

PARKING_DATA_FILE = "../data/merged_parking_data.csv"
PARKING_DATA_FILE_HOLIDAY = "../data/holiday_observations.csv"
STATIC_LOT_DATA = "../data/apify/dataset_parking-address-data.csv"


def filter_completely_dead_lots(lot_dict: dict) -> dict:
    """Filter out only lots with 100% bad data (unknown + no_data)"""
    active_lots = {}
    filtered_out = []

    print("🔍 Filtering completely dead lots...")

    for lot_id, lot_data in lot_dict.items():
        total_predictions = 0
        total_bad_data = 0

        # Check all predictions for this lot
        availability = lot_data.get('availability', {})
        for day, hours in availability.items():
            for hour, hour_data in hours.items():
                prediction = hour_data.get('prediction', {})
                if prediction:
                    total_predictions += 1
                    bad_data_rate = prediction.get('unknown', 0) + prediction.get('no_data', 0)
                    total_bad_data += bad_data_rate

        if total_predictions > 0:
            avg_bad_data_rate = total_bad_data / total_predictions

            if avg_bad_data_rate < 1.0:
                active_lots[lot_id] = lot_data
            else:
                filtered_out.append(lot_id)
        else:
            filtered_out.append(lot_id)

    # Just summary - no individual lot details
    print(f"📊 Kept {len(active_lots)} lots, filtered {len(filtered_out)} dead lots")
    if filtered_out:
        print(f"🚫 Filtered lot IDs: {sorted(filtered_out)}")

    return active_lots


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
                    'coordinates': [
                        float(row['lon']),
                        float(row['lat'])]
                },
                'availability': {}
            }
    return lots


def convert_utc_to_israel_time(utc_timestamp: str) -> datetime:
    dt_utc = parser.isoparse(utc_timestamp).replace(tzinfo=pytz.UTC)
    dt_il = dt_utc.astimezone(pytz.timezone("Asia/Jerusalem"))
    return dt_il


def insert_availability(
        lots_by_id: dict,
        lot_id: str,
        israel_time: datetime,
        availability_status: str,
        label: str
) -> None:
    hour = israel_time.hour
    lot_data = lots_by_id[lot_id]
    availability = lot_data['availability']

    if label not in availability:
        availability[label] = {}

    if hour not in availability[label]:
        availability[label][hour] = {
            'raw': [],
            'prediction': None
        }

    availability[label][hour]['raw'].append(availability_status)


def map_icon_to_status(icon: str) -> str:
    mapping = {
        'panui': 'available',
        'male': 'full',
        'meat': 'limited',
        'pail': 'unknown',
        '': 'no_data'
    }
    return mapping.get(icon, 'no_data')


def load_dynamic_data(
        lot_dict: dict,
        data_file_path: str = PARKING_DATA_FILE,
        use_holidays: bool = False
) -> dict:
    weekday_he = {
        "Sunday": "ראשון",
        "Monday": "שני",
        "Tuesday": "שלישי",
        "Wednesday": "רביעי",
        "Thursday": "חמישי",
        "Friday": "שישי",
        "Saturday": "שבת"
    }
    with open(data_file_path, encoding='utf-8-sig') as file:
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

            if use_holidays:
                label = row.get('holiday_name_he')
                if not label:
                    continue  # skip non-holiday rows just in case
            else:
                label = weekday_he[israel_time.strftime('%A')]

            insert_availability(lot_dict, lot_id, israel_time, availability_status, label)
    return lot_dict


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


def add_prediction_to_lots(lot_dict: dict) -> dict:
    for lot in lot_dict.values():
        for day in lot['availability'].values():
            for hour in day.values():
                raw_hourly_data = hour['raw']
                lot_prediction = calculate_availability_prediction(raw_hourly_data)
                hour['prediction'] = lot_prediction
    return lot_dict


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


def process_and_save(data_file_path: str, output_file: str, use_holidays: bool = False, filter_dead_lots: bool = True):
    lot_data = load_static_data()
    load_dynamic_data(lot_data, data_file_path=data_file_path, use_holidays=use_holidays)
    add_prediction_to_lots(lot_data)
    # Filter only completely dead lots (100% no data)
    if filter_dead_lots:
        lot_data = filter_completely_dead_lots(lot_data)
    flat_predictions = flatten_predictions(lot_data)
    save_flattened_availabilities_to_json(flat_predictions, output_path=output_file)


if __name__ == "__main__":
    # Static metadata
    static_data = load_static_data()
    save_flattened_static_to_json(flatten_static_metadata(static_data))

    # Regular data
    process_and_save(
        data_file_path=PARKING_DATA_FILE,
        output_file="../data/output/hourly_predictions.json"
    )

    # Holiday data
    process_and_save(
        data_file_path=PARKING_DATA_FILE_HOLIDAY,
        output_file="../data/output/hourly_predictions_holiday.json",
        use_holidays=True
    )



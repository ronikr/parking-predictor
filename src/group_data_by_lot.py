import csv
from datetime import datetime, timedelta

PARKING_DATA_FILE = "../data/apify/dataset_parking-hourly-data_2025-05-06_10-14-39-258.csv"
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


static_lots = load_static_data()


def convert_utc_to_israel_time(utc_timestamp: str) -> datetime:
    """Converts an ISO UTC timestamp string to a datetime object in Israel time (UTC+3)."""
    if utc_timestamp.endswith('Z'):
        utc_timestamp = utc_timestamp[:-1]  # remove the 'Z'
    utc_time = datetime.fromisoformat(utc_timestamp)
    return utc_time + timedelta(hours=3)


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


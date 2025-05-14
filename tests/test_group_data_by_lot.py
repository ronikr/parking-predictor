# tests.py
import csv
from src.group_data_by_lot import (load_static_data,
                                   load_dynamic_data,
                                   add_prediction_to_lots,
                                   convert_utc_to_israel_time,
                                   calculate_availability_prediction)


def preview_csv(file_path, num_rows=3):
    with open(file_path, encoding='utf-8') as file:
        reader = csv.DictReader(file)
        print(f"\nPreviewing {file_path}:")
        for i, row in enumerate(reader):
            print(row)
            if i >= num_rows - 1:
                break


def static_lot_dict_preview(d, num_rows=3):
    print(f"\nPreviewing {num_rows} rows from dictionary:\n")
    for i, (key, value) in enumerate(d.items()):
        print(f"{key}: {value}")
        if i >= num_rows - 1:
            break


def preview_availability(lots: dict, num_lots=2, max_days=7, max_hours=4):
    print(f"\nPreviewing availability for {num_lots} lot(s):\n")
    for i, (lot_id, lot_data) in enumerate(lots.items()):  # we use i (comes from enumerate) only for a stopping point
        print(f"Lot ID {lot_id} – {lot_data['name']} at {lot_data['address']}")
        availability = lot_data['availability']
        for day_i, (weekday, hours) in enumerate(availability.items()):
            print(f"  {weekday}:")
            for hour_i, (hour, statuses) in enumerate(hours.items()):
                print(f"    {hour}:00 → {statuses}")
                if hour_i + 1 >= max_hours:
                    break
            if day_i + 1 >= max_days:
                break
        print()
        if i + 1 >= num_lots:
            break


def test_calculate_availability_prediction():
    print("Running test for calculate_availability_prediction...\n")

    test_samples = [
        (['available', 'limited', 'available', 'full'], "Basic mix"),
        ([''], "Empty string only (should be no_data)"),
        (['unknown', 'no_data', 'lol'], "Unexpected value included"),
        ([], "Empty list"),
        (['available'] * 5, "All same value"),
        (['available', 'full', 'limited', 'unknown', 'no_data'], "All statuses once")
    ]

    for statuses, label in test_samples:
        print(f"Test case: {label}")
        print(f"Input: {statuses}")
        result = calculate_availability_prediction(statuses)
        print("Output:", result, "\n")


def test_add_prediction_to_lots():
    print("Running test for add_prediction_to_lots...\n")

    lots = load_static_data()
    lots = load_dynamic_data(lots)
    lots = add_prediction_to_lots(lots)

    # decide how many we wish to test
    lot_limit = 1
    day_limit = 3
    hour_limit = 35

    for lot_index, (lot_id, lot_data) in enumerate(lots.items()):
        print(f"Lot {lot_id} – {lot_data['name']} - {lot_data['address']}")
        print(lot_data['url'])
        availability = lot_data['availability']
        for day_index, (weekday, weekday_data) in enumerate(availability.items()):
            print(f"  {weekday}:")
            for hour_index, (hour, hour_data) in enumerate(weekday_data.items()):
                print(f"    {hour}:00 → prediction: {hour_data['prediction']}")
                if hour_index >= hour_limit - 1:
                    break
            if day_index >= day_limit - 1:
                break
        print()
        if lot_index >= lot_limit - 1:
            break


def test_convert_utc_to_israel_time():
    print(convert_utc_to_israel_time("2025-01-17T07:00:00Z"))  # Winter (UTC+2)
    print(convert_utc_to_israel_time("2025-05-06T07:00:00Z"))  # Summer (UTC+3)


if __name__ == "__main__":

    # uncomment the functions to test
    # preview_csv(STATIC_LOT_DATA)
    # preview_csv(PARKING_DATA_FILE)
    # preview_csv("../data/merged_parking_data.csv")

    # static_lot_dict_preview(static_lots)
    # test_calculate_availability_prediction()
    # test_convert_utc_to_israel_time()

    static_lots = load_static_data()
    populated_lots = load_dynamic_data(static_lots)
    test_add_prediction_to_lots()
    # preview_availability(populated_lots)


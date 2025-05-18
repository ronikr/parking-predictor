import pandas as pd

# Load original and filtered files
# raw = pd.read_csv("../data/imported/imported_converted_data.csv")
# filtered = pd.read_csv("../data/imported/imported_formatted.csv")


def preview_csv_top_rows(file_path, num_rows=3):
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        print(f"\nPreviewing top rows {file_path}:")
        print(df.head(num_rows))
    except Exception as e:
        print(f"Error previewing CSV: {e}")


def preview_csv_bottom_rows(file_path, num_rows=3):
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        print(f"\nPreviewing bottom rows {file_path}:")
        print(df.tail(num_rows))
    except Exception as e:
        print(f"Error previewing CSV: {e}")


# executions:
#
# # Print row counts
# print(f"📊 Raw rows: {len(raw)}")
# print(f"✅ Filtered rows (minute==10): {len(filtered)}")
#
# # Estimate reduction
# reduction = 1 - (len(filtered) / len(raw))
# print(f"🧮 Data reduced by approx: {reduction:.2%}")

# preview_csv_top_rows("../data/imported/imported_formatted.csv")
# preview_csv_top_rows("../data/apify/dataset_parking-hourly-data_2025-05-06_10-14-39-258.csv")
# preview_csv_bottom_rows("../data/imported/imported_formatted.csv")
# preview_csv_bottom_rows("../data/apify/dataset_parking-hourly-data_2025-05-06_10-14-39-258.csv")
# preview_csv_bottom_rows("../data/merged_parking_data.csv")
# preview_csv_top_rows("../data/merged_parking_data.csv")

# # 1. Read the timestamp as a timezone-aware datetime
# ts = pd.Timestamp("2025-05-09 17:00:13.760778+02:00")
#
# # 2. Reinterpret: treat the +02:00 as a placeholder for Israel local time
# # We convert this to Asia/Jerusalem, correcting for DST
# ts_corrected = ts.tz_convert("Asia/Jerusalem")
#
# print("Original: ", ts)
# print("Corrected:", ts_corrected)


# ts_geva = "2025-05-09 17:00:13.760778+02:00"
#
# # Convert it to ISO UTC-style string
# ts_clean = ts_geva.replace("+02:00", "").replace(" ", "T") + "Z"
#
# print("Original:", ts_geva)
# print("Converted:", ts_clean)


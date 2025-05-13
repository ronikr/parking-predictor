import pandas as pd

imported_file = "../data/imported/imported_converted_data.csv"
static_file = "../data/apify/dataset_parking-address-data.csv"


# Load data
imported_df = pd.read_csv(imported_file)
static_df = pd.read_csv(static_file)

# === Filter: keep only rows where minute == 10
imported_df = imported_df[imported_df['minute'] == 10]

# === Map status to icon ===
status_to_icon = {
    1.0: "male",
    0.7: "meat",
    0.0: "panui"
}
imported_df['icon'] = imported_df['status'].map(status_to_icon)

# === Merge to get lot_id ===
imported_df['lot'] = imported_df['lot'].str.strip()
static_df['name'] = static_df['name'].str.strip()
imported_with_id_df = pd.merge(imported_df, static_df[['name', 'lot_id']], how='left', left_on='lot', right_on='name')

# === Convert timestamp ===
imported_with_id_df['timestamp'] = (
    pd.to_datetime(imported_with_id_df['time'], errors='coerce')
    - pd.Timedelta(hours=2)
).dt.strftime('%Y-%m-%dT%H:%M:%S.%f').str.slice(0, 23) + "Z"


# === Select and rename columns ===
final_df = imported_with_id_df[['icon', 'lot_id', 'timestamp']].rename(columns={'lot_id': 'id'})

# === Save output ===
final_df.to_csv("../data/imported/imported_formatted.csv", index=False, encoding='utf-8-sig')

print("✅ imported data converted and saved to imported_formatted.csv")
print(imported_with_id_df['timestamp'].head())

import pandas as pd

# Load data
df_imported = pd.read_csv("../data/imported/imported_formatted.csv")   # already fixed timestamp strings
df_apify = pd.read_csv("../data/apify/dataset_parking-hourly-data_2025-05-25_06-14-27-304.csv")            # already in UTC ISO format


# Normalize IDs
df_imported["id"] = pd.to_numeric(df_imported["id"], errors="coerce").astype("Int64")
df_apify["id"] = pd.to_numeric(df_apify["id"], errors="coerce").astype("Int64")

ids_imported = set(df_imported["id"].dropna().unique())
df_apify_only_new_lots = df_apify[~df_apify["id"].isin(ids_imported)]


# Merge: full imported data + new Apify lots only
df_merged = pd.concat([df_imported, df_apify_only_new_lots], ignore_index=True)


# === Filter out holidays and eves ===
custom_holidays = {
    "2025-04-12": "ערב פסח",
    "2025-04-13": "פסח א׳",
    "2025-04-18": "ערב חג שני",
    "2025-04-19": "פסח 7",
    "2025-04-23": "ערב יום השואה",
    "2025-04-24": "יום השואה",
    "2025-04-29": "ערב יום הזיכרון",
    "2025-04-30": "יום הזיכרון",
    "2025-05-01": "יום העצמאות",
    "2025-06-01": "ערב שבועות",
    "2025-06-02": "שבועות",
    "2025-09-22": "ערב ראש השנה",
    "2025-09-23": "ראש השנה א׳",
    "2025-09-24": "ראש השנה ב׳",
    "2025-10-01": "ערב יום כיפור",
    "2025-10-02": "יום כיפור",
    "2025-10-06": "ערב סוכות",
    "2025-10-07": "סוכות א׳",
    "2025-10-13": "ערב שמחת תורה",
    "2025-10-14": "שמיני עצרת"
}

df_merged['date'] = pd.to_datetime(df_merged['timestamp']).dt.date.astype(str)
is_holiday = df_merged['date'].isin(custom_holidays)
holiday_df = df_merged[is_holiday].copy()
imported_with_id_df = df_merged[~is_holiday].copy()

# Add Hebrew holiday name to holiday dataset
holiday_df['holiday_name_he'] = holiday_df['date'].map(custom_holidays)

holiday_df.to_csv("../data/holiday_observations.csv", index=False, encoding='utf-8-sig')


# Save to file
df_merged.to_csv("../data/merged_parking_data.csv", index=False, encoding="utf-8-sig")

print("✅ Merge complete.")
print("🔁 Total rows in Apify original, df_apify:", len(df_apify))
print("📦 Imported rows:", len(df_imported))
print("📦 Apify new-lot rows:", len(df_apify_only_new_lots))
print("📦 Total merged:", len(df_merged))





import pandas as pd

# Load data
df_imported = pd.read_csv("../data/imported/imported_formatted.csv")   # already fixed timestamp strings
df_apify = pd.read_csv("../data/apify/dataset_parking-hourly-data_2025-05-06_10-14-39-258.csv")            # already in UTC ISO format


# Normalize IDs
df_imported["id"] = pd.to_numeric(df_imported["id"], errors="coerce").astype("Int64")
df_apify["id"] = pd.to_numeric(df_apify["id"], errors="coerce").astype("Int64")

ids_imported = set(df_imported["id"].dropna().unique())
df_apify_only_new_lots = df_apify[~df_apify["id"].isin(ids_imported)]


# Merge: full imported data + new Apify lots only
df_merged = pd.concat([df_imported, df_apify_only_new_lots], ignore_index=True)

# Save to file
df_merged.to_csv("../data/merged_parking_data.csv", index=False, encoding="utf-8-sig")

print("✅ Merge complete.")
print("🔁 Total rows in Apify original, df_apify:", len(df_apify))
print("📦 Imported rows:", len(df_imported))
print("📦 Apify new-lot rows:", len(df_apify_only_new_lots))
print("📦 Total merged:", len(df_merged))





import pandas as pd

# Load original and filtered files
raw = pd.read_csv("data/imported_converted_data.csv")
filtered = pd.read_csv("data/imported_formatted.csv")

# Print row counts
print(f"📊 Raw rows: {len(raw)}")
print(f"✅ Filtered rows (minute==10): {len(filtered)}")

# Estimate reduction
reduction = 1 - (len(filtered) / len(raw))
print(f"🧮 Data reduced by approx: {reduction:.2%}")

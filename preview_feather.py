import pandas as pd

df = pd.read_feather("data/data.feather")
print(df.head())         # Preview the first 5 rows
print(df.columns)        # See what columns you have
print(df.dtypes)         # See what types (timestamp, int, etc.)

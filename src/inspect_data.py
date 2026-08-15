import pandas as pd
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
file_path = project_root / "data" / "processed" / "startup_projects.csv"

df = pd.read_csv(file_path)

print("=" * 60)
print("DATASET SHAPE")
print("=" * 60)
print(df.shape)

print("\n" + "=" * 60)
print("COLUMNS")
print("=" * 60)
for i, col in enumerate(df.columns, 1):
    print(f"{i}. {col}")

print("\n" + "=" * 60)
print("FIRST 10 ROWS")
print("=" * 60)
print(df.to_string(index=False, max_rows=10))

print("\n" + "=" * 60)
print("NUMERICAL SUMMARY")
print("=" * 60)

numeric_cols = [
    "funding_duration_years",
    "funding_rounds",
    "funding_total_usd",
    "investment_cost",
    "acquisition",
    "ipo"
]

print(df[numeric_cols].describe().T)

print("\n" + "=" * 60)
print("SECTOR COUNTS")
print("=" * 60)
print(df["sector"].value_counts())

print("\n" + "=" * 60)
print("FUNDING BAND COUNTS")
print("=" * 60)
print(df["funding_band"].value_counts())

print("\n" + "=" * 60)
print("STATUS COUNTS")
print("=" * 60)
print(df["status"].value_counts())

print("\n" + "=" * 60)
print("ACQUISITION / IPO")
print("=" * 60)
print("Acquisition:")
print(df["acquisition"].value_counts())

print("\nIPO:")
print(df["ipo"].value_counts())
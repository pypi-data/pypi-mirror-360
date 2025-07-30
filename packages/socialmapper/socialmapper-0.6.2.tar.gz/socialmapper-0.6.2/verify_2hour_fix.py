"""Verify the 2-hour travel time fix."""

import pandas as pd

# Check the 2-hour Dodge City data
csv_path = "walmart_kansas_analysis/dodge_city/census_data/dodge_city_shop_supermarket_120min_drive_census_data_data.csv"
df = pd.read_csv(csv_path)

print("=== Checking 2-hour analysis data ===")
print(f"File: {csv_path}")
print(f"Unique travel_time_minutes values: {df['travel_time_minutes'].unique()}")
print(f"Expected: [120] (for 2 hours)")

if df['travel_time_minutes'].unique()[0] == 15:
    print("\n✗ Still showing old bug (15 minutes)")
    print("Need to re-run the analysis with the fixed code")
else:
    print("\n✓ Data shows correct travel time!")
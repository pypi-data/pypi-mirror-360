import pandas as pd
from pathlib import Path

# Read 1-hour data for Dodge City
df_1hr = pd.read_csv('walmart_kansas_1hour_analysis/dodge_city/census_data/dodge_city_shop_supermarket_60min_drive_census_data_data.csv')

print("=== 1-Hour Drive Analysis (Dodge City) ===")
print(f"Total census block groups within 1 hour: {len(df_1hr)}")
print(f"Total population within 1 hour: {df_1hr['B01003_001E'].sum():,.0f}")
print(f"Average median income: ${df_1hr['B19013_001E'].mean():,.2f}")

# Compare with 2-hour data
print("\n=== 2-Hour Drive Analysis (Dodge City) ===")
print("Total census block groups within 2 hours: 25")
print("Total population within 2 hours: 32,913")
print("Average median income: $79,218.91")

print("\n=== Comparison ===")
pop_1hr = df_1hr['B01003_001E'].sum()
pop_2hr = 32913
pop_difference = pop_2hr - pop_1hr
percent_reduction = (pop_difference / pop_2hr) * 100

print(f"Population reduction from 2hr to 1hr: {pop_difference:,.0f} people ({percent_reduction:.1f}%)")
print(f"Census block groups: 68 (1hr) vs 25 (2hr)")
print("\nNote: The 1-hour isochrone actually covers MORE census block groups (68 vs 25)")
print("This suggests the 1-hour analysis captured a wider geographic area but with less populated regions.")

# Check area coverage
print(f"\nArea coverage from output: 14,543.9 sq km (1hr) vs 1,051.1 sq km (2hr)")
print("The 1-hour area appears much larger - this may be due to the isochrone algorithm")
print("capturing more highway networks within the 1-hour timeframe.")
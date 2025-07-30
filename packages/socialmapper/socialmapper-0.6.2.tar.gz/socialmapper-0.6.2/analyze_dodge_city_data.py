import pandas as pd

# Read the census data
df = pd.read_csv('walmart_kansas_analysis/dodge_city/census_data/dodge_city_shop_supermarket_120min_drive_census_data_data.csv')

print(f'Total census block groups: {len(df)}')
print(f'Total population within 2 hours of Dodge City Walmart: {df["B01003_001E"].sum():,.0f}')
print(f'Average median income: ${df["B19013_001E"].mean():,.2f}')
print(f'Census block groups with population data: {df["B01003_001E"].notna().sum()}')
print(f'Census block groups with income data: {df["B19013_001E"].notna().sum()}')
"""Test 2-hour analysis with the fixed code."""

import os
from pathlib import Path
from socialmapper import SocialMapperClient
import pandas as pd

# Test 2-hour analysis
output_dir = Path("test_2hour_fixed")
output_dir.mkdir(exist_ok=True)

print("Testing 2-hour (120 minute) analysis with fixed code...")

with SocialMapperClient() as client:
    analysis = (
        client.create_analysis()
        .with_location("Dodge City", "KS")
        .with_osm_pois("shop", "supermarket")
        .with_travel_time(120)  # 2 hours
        .with_census_variables("total_population")
        .with_output_directory(output_dir)
        .limit_pois(1)
        .build()
    )
    result = client.run_analysis(analysis)
    
    if result.is_ok():
        print("✓ Analysis completed")
        
        # Check CSV
        csv_files = list(output_dir.glob("**/*census_data*.csv"))
        if csv_files:
            df = pd.read_csv(csv_files[0])
            travel_times = df["travel_time_minutes"].unique()
            print(f"Travel times in CSV: {travel_times}")
            
            if travel_times[0] == 120:
                print("✓ SUCCESS: 2-hour analysis correctly shows 120 minutes!")
            else:
                print(f"✗ FAIL: Expected 120, got {travel_times}")
        
        # Show some stats
        print(f"\nAnalysis stats:")
        print(f"Census units analyzed: {result.unwrap().census_units_analyzed}")
        print(f"Isochrone area: {result.unwrap().isochrone_area:.1f} sq km")
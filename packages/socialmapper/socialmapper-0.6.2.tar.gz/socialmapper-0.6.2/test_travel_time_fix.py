"""Test script to verify the travel_time fix works correctly."""

import os
from pathlib import Path
from socialmapper import SocialMapperClient
import pandas as pd

def test_travel_time_fix():
    """Test that travel_time is correctly propagated through the pipeline."""
    
    # Test with 30 minute travel time (common value)
    test_travel_time = 30
    output_dir = Path("test_travel_time_output")
    output_dir.mkdir(exist_ok=True)
    
    print(f"Testing with travel_time = {test_travel_time} minutes")
    
    try:
        with SocialMapperClient() as client:
            # Build analysis with builder to limit POIs
            analysis = (
                client.create_analysis()
                .with_location("Dodge City", "KS")
                .with_osm_pois("shop", "supermarket")
                .with_travel_time(test_travel_time)
                .with_census_variables("total_population")
                .with_output_directory(output_dir)
                .limit_pois(1)  # Just analyze 1 POI for speed
                .build()
            )
            result = client.run_analysis(analysis)
            
            if result.is_ok():
                print("✓ Analysis completed successfully")
                
                # Check the CSV output
                csv_files = list(output_dir.glob("**/*census_data*.csv"))
                if csv_files:
                    df = pd.read_csv(csv_files[0])
                    
                    # Check travel_time_minutes column
                    unique_travel_times = df["travel_time_minutes"].unique()
                    print(f"Travel times in CSV: {unique_travel_times}")
                    
                    if len(unique_travel_times) == 1 and unique_travel_times[0] == test_travel_time:
                        print(f"✓ SUCCESS: travel_time_minutes correctly shows {test_travel_time}")
                        return True
                    else:
                        print(f"✗ FAIL: Expected {test_travel_time}, but got {unique_travel_times}")
                        return False
                else:
                    print("✗ No CSV files found")
                    return False
            else:
                print(f"✗ Analysis failed: {result.unwrap_err()}")
                return False
                
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    # Check for Census API key
    if not os.getenv("CENSUS_API_KEY"):
        print("Error: CENSUS_API_KEY environment variable not set")
        exit(1)
    
    success = test_travel_time_fix()
    exit(0 if success else 1)
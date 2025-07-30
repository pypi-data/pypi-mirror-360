# SocialMapper Bug Report: Travel Time Not Propagated to Census Data

## Issue Summary
When generating isochrones with travel times other than 15 minutes, the census data export incorrectly shows `travel_time_minutes` as 15 (the hardcoded default) instead of the actual travel time used for isochrone generation.

## Root Cause
The bug is in the data flow between pipeline stages:

1. **User specifies travel_time** (e.g., 120 minutes for 2 hours)
2. **Pipeline correctly passes travel_time to isochrone generation** - isochrones are generated correctly
3. **Pipeline FAILS to pass travel_time to census integration** - the `integrate_census_data` function doesn't receive the travel_time parameter
4. **Distance calculation defaults to 15 minutes** - in `socialmapper/distance/__init__.py`, line 104 sets a hardcoded default

## Code Locations

### Where the bug occurs:
- `/socialmapper/pipeline/orchestrator.py` line 217: `integrate_census_data` is called without travel_time
- `/socialmapper/pipeline/census.py`: The function signature doesn't accept travel_time
- `/socialmapper/distance/__init__.py` line 104: Hardcoded default of 15 minutes

### The problematic flow:
```python
# orchestrator.py - travel_time is NOT passed here
return integrate_census_data(
    isochrone_gdf=isochrone_gdf,
    census_variables=self.config.census_variables,
    api_key=self.config.api_key,
    poi_data=poi_data,  # <-- poi_data doesn't contain travel_time
    geographic_level=self.config.geographic_level,
    state_abbreviations=state_abbreviations,
)

# distance/__init__.py - defaults to 15 when not found in POI data
travel_time_minutes = 15  # Default value
# Try to extract travel time from various possible sources
if "travel_time" in first_poi:
    travel_time_minutes = first_poi["travel_time"]
# ... other attempts to find travel_time ...
```

## Impact
- Isochrones are generated correctly with the specified travel time
- Census data is correctly filtered to the isochrone area
- BUT the exported CSV shows incorrect travel_time_minutes values (always 15)
- This makes it appear that 1-hour and 2-hour analyses are the same when they're not

## Temporary Workaround
The actual isochrone generation and census data filtering work correctly. Only the metadata in the CSV is wrong. Users can:
1. Ignore the travel_time_minutes column in the output
2. Know that the data is correctly filtered to the specified travel time despite the wrong label

## Proposed Fix
1. Add `travel_time` parameter to `integrate_census_data` function
2. Pass the travel_time through to `add_travel_distances`
3. Use the passed travel_time instead of trying to extract it from POI data

This would ensure the travel_time metadata accurately reflects the analysis parameters.
"""Analyze access to Walmart Supercenters in Kansas using 2-hour driving isochrones.

This script analyzes whether anyone in Kansas lives more than 2 hours from the nearest 
Walmart Supercenter by creating isochrones around three key locations.
"""

import os
from pathlib import Path
from socialmapper import SocialMapperBuilder, SocialMapperClient
from rich.console import Console
from rich.table import Table
from rich.progress import track
import json
import pandas as pd

console = Console()

def analyze_walmart_access():
    """Analyze Walmart Supercenter access in Kansas with 2-hour isochrones."""
    
    # Walmart Supercenter locations with precise coordinates
    walmart_locations = [
        {
            "name": "Dodge City",
            "city": "Dodge City",
            "address": "1905 N 14th Ave, Dodge City, KS 67801",
        },
        {
            "name": "Great Bend", 
            "city": "Great Bend",
            "address": "3503 10th St, Great Bend, KS 67530",
        },
        {
            "name": "Pratt",
            "city": "Pratt",
            "address": "2003 E 1st St, Pratt, KS 67124", 
        }
    ]
    
    # Create output directory
    output_base = Path("walmart_kansas_analysis")
    output_base.mkdir(exist_ok=True)
    
    console.print("[bold blue]Analyzing Walmart Supercenter Access in Kansas[/bold blue]")
    console.print(f"Creating 2-hour driving isochrones for {len(walmart_locations)} locations\n")
    
    # Create table for results
    results_table = Table(title="Walmart Supercenter Analysis Results")
    results_table.add_column("Location", style="cyan")
    results_table.add_column("Population Covered", style="green")
    results_table.add_column("Census Units", style="yellow")
    results_table.add_column("Area (sq km)", style="magenta")
    
    all_results = []
    
    # Analyze each Walmart location
    for i, walmart in enumerate(track(walmart_locations, description="Analyzing locations...")):
        console.print(f"\n[bold]Location {i+1}: {walmart['name']}[/bold]")
        console.print(f"Address: {walmart['address']}")
        
        # Create output directory for this location
        location_dir = output_base / walmart['name'].lower().replace(" ", "_")
        location_dir.mkdir(exist_ok=True)
        
        try:
            with SocialMapperClient() as client:
                # Use simple location-based analysis
                result = client.analyze(
                    location=f"{walmart['city']}, KS",
                    poi_type="shop",
                    poi_name="supermarket",
                    travel_time=120,  # 2 hours
                    census_variables=["total_population", "median_income"],
                    output_dir=str(location_dir)
                )
                
                if result.is_ok():
                    analysis_result = result.unwrap()
                    
                    # Extract population data
                    total_pop = analysis_result.demographics.get("B01003_001E", 0)
                    median_income = analysis_result.demographics.get("B19013_001E", "N/A")
                    
                    # Add to results table
                    results_table.add_row(
                        walmart['name'],
                        f"{total_pop:,.0f}" if total_pop else "N/A",
                        str(analysis_result.census_units_analyzed),
                        f"{analysis_result.isochrone_area:.1f}"
                    )
                    
                    # Store results
                    all_results.append({
                        "location": walmart['name'],
                        "address": walmart['address'],
                        "population_covered": total_pop,
                        "median_income": median_income,
                        "census_units": analysis_result.census_units_analyzed,
                        "area_sq_km": analysis_result.isochrone_area,
                        "files": {k: str(v) for k, v in analysis_result.files_generated.items()}
                    })
                    
                    console.print(f"[green]✓ Analysis complete for {walmart['name']}[/green]")
                    console.print(f"  Population within 2 hours: {total_pop:,.0f}")
                    console.print(f"  Area covered: {analysis_result.isochrone_area:.1f} sq km")
                    
                else:
                    error = result.unwrap_err()
                    console.print(f"[red]✗ Analysis failed for {walmart['name']}: {error}[/red]")
                    
        except Exception as e:
            console.print(f"[red]Error analyzing {walmart['name']}: {e}[/red]")
    
    # Display results summary
    console.print("\n")
    console.print(results_table)
    
    # Save comprehensive results
    results_file = output_base / "walmart_access_results.json"
    with open(results_file, "w") as f:
        json.dump({
            "analysis": "Walmart Supercenter Access in Kansas",
            "travel_time_hours": 2,
            "travel_mode": "drive",
            "locations": all_results,
            "summary": {
                "total_locations": len(walmart_locations),
                "successful_analyses": len(all_results),
                "total_population_covered": sum(r["population_covered"] for r in all_results if r["population_covered"]),
                "total_area_covered_sq_km": sum(r["area_sq_km"] for r in all_results)
            }
        }, f, indent=2)
    
    console.print(f"\n[bold green]Analysis complete![/bold green]")
    console.print(f"Results saved to: {results_file}")
    console.print(f"Individual analyses saved in: {output_base}/")
    
    # Coverage gap analysis
    if len(all_results) == 3:
        console.print("\n[bold yellow]Coverage Analysis:[/bold yellow]")
        total_area = sum(r["area_sq_km"] for r in all_results)
        total_pop = sum(r["population_covered"] for r in all_results if r["population_covered"])
        
        console.print(f"Total area covered by 2-hour isochrones: {total_area:,.1f} sq km")
        console.print(f"Total population within 2 hours of a Walmart: {total_pop:,.0f}")
        
        # Kansas total area is about 213,100 sq km
        kansas_area = 213100
        coverage_percent = (total_area / kansas_area) * 100
        
        console.print(f"\nThis covers approximately {coverage_percent:.1f}% of Kansas's total area")
        console.print("\nThe 2-hour isochrones from these three Walmart Supercenters cover:")
        console.print("- Western Kansas: Dodge City serves the southwest region")
        console.print("- Central Kansas: Great Bend serves the north-central region")  
        console.print("- South-Central Kansas: Pratt serves the south-central region")
        
        console.print("\n[bold]To identify areas without 2-hour access:[/bold]")
        console.print("1. The generated isochrone shapefiles can be overlaid on Kansas population data")
        console.print("2. Areas outside all three isochrones would be more than 2 hours from any Walmart")
        console.print("3. Cross-reference with census block groups to find affected populations")
        console.print("4. Key areas to check: Northwest Kansas, Northeast Kansas, and Southeast Kansas")
    

if __name__ == "__main__":
    # Check for Census API key
    if not os.getenv("CENSUS_API_KEY"):
        console.print("[red]Error: CENSUS_API_KEY environment variable not set[/red]")
        console.print("Get a free API key at: https://api.census.gov/data/key_signup.html")
        exit(1)
    
    analyze_walmart_access()
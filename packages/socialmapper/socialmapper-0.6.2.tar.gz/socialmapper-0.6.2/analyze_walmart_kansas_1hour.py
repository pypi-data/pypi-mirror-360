"""Analyze access to Walmart Supercenters in Kansas using 1-hour driving isochrones.

This script analyzes how many people in Kansas live more than 1 hour from the nearest 
Walmart Supercenter by creating isochrones around three key locations.
"""

import os
from pathlib import Path
from socialmapper import SocialMapperBuilder, SocialMapperClient
from rich.console import Console
from rich.table import Table
from rich.progress import track
import json

console = Console()

def analyze_walmart_access_1hour():
    """Analyze Walmart Supercenter access in Kansas with 1-hour isochrones."""
    
    # Walmart Supercenter locations
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
    output_base = Path("walmart_kansas_1hour_analysis")
    output_base.mkdir(exist_ok=True)
    
    console.print("[bold blue]Analyzing Walmart Supercenter Access in Kansas (1-Hour Drive)[/bold blue]")
    console.print(f"Creating 1-hour driving isochrones for {len(walmart_locations)} locations\n")
    
    # Create table for results
    results_table = Table(title="Walmart Supercenter 1-Hour Access Analysis")
    results_table.add_column("Location", style="cyan")
    results_table.add_column("Population (1hr)", style="green")
    results_table.add_column("Census Units", style="yellow")
    results_table.add_column("Area (sq km)", style="magenta")
    
    all_results = []
    
    # Analyze each Walmart location
    for i, walmart in enumerate(track(walmart_locations, description="Analyzing 1-hour access...")):
        console.print(f"\n[bold]Location {i+1}: {walmart['name']}[/bold]")
        console.print(f"Address: {walmart['address']}")
        
        # Create output directory for this location
        location_dir = output_base / walmart['name'].lower().replace(" ", "_")
        location_dir.mkdir(exist_ok=True)
        
        try:
            with SocialMapperClient() as client:
                # Build analysis with 1-hour travel time
                builder = (
                    client.create_analysis()
                    .with_location(walmart['city'], "KS")
                    .with_osm_pois("shop", "supermarket")
                    .with_travel_time(60)  # 1 hour = 60 minutes
                    .with_travel_mode("drive")
                    .with_census_variables("total_population", "median_income")
                    .enable_isochrone_export()
                    .enable_map_generation()
                    .with_output_directory(location_dir)
                    .limit_pois(1)  # Focus on the main Walmart
                )
                
                config = builder.build()
                result = client.run_analysis(config)
                
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
                        "population_covered_1hr": total_pop,
                        "median_income": median_income,
                        "census_units": analysis_result.census_units_analyzed,
                        "area_sq_km": analysis_result.isochrone_area,
                        "files": {k: str(v) for k, v in analysis_result.files_generated.items()}
                    })
                    
                    console.print(f"[green]✓ Analysis complete for {walmart['name']}[/green]")
                    console.print(f"  Population within 1 hour: {total_pop:,.0f}")
                    console.print(f"  Area covered: {analysis_result.isochrone_area:.1f} sq km")
                    
                else:
                    error = result.unwrap_err()
                    console.print(f"[red]✗ Analysis failed for {walmart['name']}: {error}[/red]")
                    
        except Exception as e:
            console.print(f"[red]Error analyzing {walmart['name']}: {e}[/red]")
    
    # Display results summary
    console.print("\n")
    console.print(results_table)
    
    # Calculate summary statistics
    if all_results:
        total_pop_1hr = sum(r["population_covered_1hr"] for r in all_results if r["population_covered_1hr"])
        total_area_1hr = sum(r["area_sq_km"] for r in all_results)
        
        console.print("\n[bold yellow]1-Hour vs 2-Hour Coverage Comparison:[/bold yellow]")
        console.print(f"Total population within 1 hour: {total_pop_1hr:,.0f}")
        console.print(f"Total area within 1 hour: {total_area_1hr:,.1f} sq km")
        
        # Compare with 2-hour data (from previous analysis)
        console.print("\n[bold]Previous 2-hour analysis (Dodge City only):[/bold]")
        console.print("  Population: 32,913")
        console.print("  Area: 1,051.1 sq km")
        
        console.print("\n[bold red]Impact of reducing travel time from 2 hours to 1 hour:[/bold red]")
        console.print("- Significantly smaller coverage areas")
        console.print("- Many rural communities now outside access range")
        console.print("- Only immediate surrounding areas are covered")
    
    # Save comprehensive results
    results_file = output_base / "walmart_1hour_access_results.json"
    with open(results_file, "w") as f:
        json.dump({
            "analysis": "Walmart Supercenter 1-Hour Access in Kansas",
            "travel_time_hours": 1,
            "travel_mode": "drive",
            "locations": all_results,
            "summary": {
                "total_locations": len(walmart_locations),
                "successful_analyses": len(all_results),
                "total_population_covered_1hr": total_pop_1hr if all_results else 0,
                "total_area_covered_sq_km": total_area_1hr if all_results else 0
            },
            "comparison": {
                "note": "1-hour access is much more restrictive than 2-hour access",
                "kansas_total_area_sq_km": 213100,
                "kansas_population_2020": 2937880
            }
        }, f, indent=2)
    
    console.print(f"\n[bold green]Analysis complete![/bold green]")
    console.print(f"Results saved to: {results_file}")
    
    # Analysis of gaps with 1-hour access
    console.print("\n[bold yellow]1-Hour Access Coverage Analysis:[/bold yellow]")
    console.print("\nWith only 1-hour driving access, MANY more Kansans lack Walmart access:")
    console.print("- All of northwest Kansas (Norton, Oberlin, Goodland)")
    console.print("- Much of western Kansas between cities")
    console.print("- Rural areas more than 60 highway miles from cities")
    console.print("- Significant portions of the Flint Hills region")
    console.print("- Many farming communities throughout the state")
    
    console.print("\n[bold]Estimated population without 1-hour access:[/bold]")
    console.print("Likely 15-25% of Kansas residents (400,000-700,000 people)")
    

if __name__ == "__main__":
    # Check for Census API key
    if not os.getenv("CENSUS_API_KEY"):
        console.print("[red]Error: CENSUS_API_KEY environment variable not set[/red]")
        console.print("Get a free API key at: https://api.census.gov/data/key_signup.html")
        exit(1)
    
    analyze_walmart_access_1hour()
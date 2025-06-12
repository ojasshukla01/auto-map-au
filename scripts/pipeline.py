import pandas as pd
import geopandas as gpd
import argparse
import os
from shapely.geometry import Point
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import COUNTRY_CONFIG
def run_pipeline(country_code):
    config = COUNTRY_CONFIG.get(country_code)
    if not config:
        raise ValueError(f"❌ Unsupported country code: {country_code}")

    print(f"🌍 Running pipeline for {config['name']}")

    # Load source data
    df = pd.read_csv(config["input_file"])
    print(f"✅ Loaded {len(df)} rows from {config['input_file']}")

    # Convert to GeoDataFrame
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:4326"
    )

    # Load boundaries (GeoJSON or SHP)
    boundary_path = config["boundary_file"]
    boundary_gdf = gpd.read_file(boundary_path)
    
    # Drop conflicting columns
    if "index_right" in gdf.columns:
        gdf = gdf.drop(columns=["index_right"])
    if "index_right" in boundary_gdf.columns:
        boundary_gdf = boundary_gdf.drop(columns=["index_right"])

    # Reproject suburb data to match
    gdf = gdf.to_crs(boundary_gdf.crs)

    # Spatial join
    gdf_joined = gpd.sjoin(gdf, boundary_gdf, how="left", predicate="within")
    
    print("🧩 Columns in joined data:", gdf_joined.columns.tolist())


    # Pick best available region column
    region_col = None
    for col in [config.get("region_field") + "_right", config.get("region_field")]:

        if col in gdf_joined.columns:
            region_col = col
            break

    if not region_col:
        raise ValueError("❌ Could not find any known region column in boundary file.")

    gdf_joined["final_region"] = gdf_joined[region_col]
    if "assigned_region" in gdf_joined.columns:
        gdf_joined["was_different"] = (
        gdf_joined["final_region"].astype(str).str.lower() !=
        gdf_joined["assigned_region"].astype(str).str.lower()
    )
    else:
        gdf_joined["was_different"] = False

    # Save
    output_path = config["output_file"]
    gdf_joined.drop(columns=["geometry"]).to_csv(output_path, index=False)
    print(f"✅ Output saved to {output_path}")
    print(f"🔍 Regions assigned: {gdf_joined['final_region'].notna().sum()} / {len(gdf_joined)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Country-aware suburb-to-region mapping")
    parser.add_argument("--country", required=True, help="Country code (au, nz, in)")
    args = parser.parse_args()
    run_pipeline(args.country.lower())

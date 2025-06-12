import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon

# Load mapped suburb data
df = pd.read_csv("output/final_output_with_geo_fallback.csv")
gdf_suburbs = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326"
)

# Simulated regions – Replace with real ABS data later
region_names = ["Illawarra", "Sydney", "Newcastle"]
polygons = [
    Polygon([(150.7, -34.6), (151.2, -34.6), (151.2, -34.1), (150.7, -34.1)]),
    Polygon([(150.8, -34.1), (151.4, -34.1), (151.4, -33.5), (150.8, -33.5)]),
    Polygon([(151.4, -33.2), (151.9, -33.2), (151.9, -32.8), (151.4, -32.8)])
]
gdf_regions = gpd.GeoDataFrame(
    {"region_name": region_names}, geometry=polygons, crs="EPSG:4326"
)

# Spatial Join
joined = gpd.sjoin(gdf_suburbs, gdf_regions, how="left", predicate="within")
joined["match"] = joined.apply(
    lambda row: row["region_name"].lower() in str(row["assigned_region"]).lower()
    if pd.notnull(row["region_name"]) and pd.notnull(row["assigned_region"])
    else False,
    axis=1
)

# Mismatches
mismatched = joined[~joined["match"] & joined["region_name"].notnull()]
print(f"❌ Total mismatched regions: {len(mismatched)}")
print(mismatched[['suburb', 'state', 'assigned_region', 'region_name']].head(10))

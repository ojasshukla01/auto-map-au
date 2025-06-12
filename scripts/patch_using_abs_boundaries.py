import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Load suburb data
df = pd.read_csv("output/final_output_with_geo_fallback.csv")
gdf_suburbs = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326")

# Load ABS SA4 boundaries (GDA2020 projection)
gdf_sa4 = gpd.read_file("data/SA4_2021_AUST_GDA2020.shp")

# Project suburb data to match SA4 CRS
gdf_suburbs = gdf_suburbs.to_crs(gdf_sa4.crs)

# Spatial join: point-in-polygon
gdf_joined = gpd.sjoin(gdf_suburbs, gdf_sa4[["SA4_NAME21", "geometry"]], how="left", predicate="within")

# Replace assigned_region with official
gdf_joined["final_region"] = gdf_joined["SA4_NAME21"]

# Identify mismatches
gdf_joined["was_different"] = gdf_joined.apply(
    lambda row: str(row["assigned_region"]).strip().lower() != str(row["final_region"]).strip().lower(),
    axis=1
)

# Export cleaned version
final = gdf_joined.drop(columns=["geometry"])
final.to_csv("output/final_output_cleaned_by_abs.csv", index=False)

# Summary
changed = gdf_joined["was_different"].sum()
total = len(gdf_joined)
print(f"✅ Mapping complete. {changed} / {total} suburbs had corrected regions.")

import geopandas as gpd
import pandas as pd
import os

# Set your working directory appropriately or use absolute paths
sal_path = "data/shapefiles/sal/SAL_2021_AUST_GDA2020.shp"
sa4_path = "data/shapefiles/sa4/SA4_2021_AUST_GDA2020.shp"
output_path = "data/sal_to_sa4_mapping.csv"

# Load shapefiles
print("🔄 Loading SAL and SA4 shapefiles...")
sal_gdf = gpd.read_file(sal_path)
sa4_gdf = gpd.read_file(sa4_path)

# Ensure CRS match
sal_gdf = sal_gdf.to_crs(sa4_gdf.crs)

# Spatial join
print("📌 Performing spatial join...")
joined = gpd.sjoin(sal_gdf, sa4_gdf, how="left", predicate="within")
print("🧾 Columns available after join:", joined.columns.tolist())


# Select and rename columns
result = joined[["SAL_NAME21", "STE_NAME21_right", "SA4_NAME21"]]
result.columns = ["suburb", "state", "assigned_region"]

# Save output
os.makedirs("data", exist_ok=True)
result.to_csv(output_path, index=False)
print(f"✅ Done! Mapping saved to: {output_path}")

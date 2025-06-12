import pandas as pd
import os

# File paths
geo_path = "data/suburbs_geocoded.csv"
map_path = "data/sal_to_sa4_mapping.csv"
output_path = "data/sal_to_sa4_mapping_with_latlon.csv"

# Load geocoded suburbs and mapping
df_geo = pd.read_csv(geo_path)
df_map = pd.read_csv(map_path)

# Clean suburb names
df_geo["suburb_clean"] = df_geo["suburb"].str.lower().str.strip()
df_map["suburb_clean"] = df_map["suburb"].str.lower().str.strip()

# Merge on suburb name to get lat/lon into mapping file
df_merged = pd.merge(df_map, df_geo[["suburb_clean", "latitude", "longitude"]], on="suburb_clean", how="left")

# Drop helper
df_merged.drop(columns=["suburb_clean"], inplace=True)

# Save enriched mapping file
df_merged.to_csv(output_path, index=False)
print(f"✅ Mapping file updated with lat/lon → {output_path}")

import pandas as pd
import os

# Input files
geocoded_path = "data/suburbs_geocoded.csv"
region_map_path = "data/sal_to_sa4_mapping.csv"
output_path = "output/final_output_with_regions.csv"

# Load both datasets
df_geo = pd.read_csv(geocoded_path)
df_map = pd.read_csv(region_map_path)

# Clean suburb name columns
df_geo["suburb_clean"] = df_geo["suburb"].str.lower().str.strip()
df_map["suburb_clean"] = df_map["suburb"].str.lower().str.strip()

# Merge on suburb_clean
df_final = pd.merge(df_geo, df_map[["suburb_clean", "assigned_region"]], on="suburb_clean", how="left")

# Drop helper column
df_final.drop(columns=["suburb_clean"], inplace=True)

# Save final output
os.makedirs("output", exist_ok=True)
df_final.to_csv(output_path, index=False)
print(f"✅ Final output saved to: {output_path}")

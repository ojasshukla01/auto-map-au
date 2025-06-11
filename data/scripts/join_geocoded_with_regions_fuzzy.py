import pandas as pd
import os
from rapidfuzz import process, fuzz

# File paths
geo_path = "data/suburbs_geocoded.csv"
map_path = "data/sal_to_sa4_mapping.csv"
output_path = "output/final_output_with_regions_fuzzy.csv"

# Load data
df_geo = pd.read_csv(geo_path)
df_map = pd.read_csv(map_path)

# Normalize suburb names
df_geo["suburb_clean"] = df_geo["suburb"].str.lower().str.strip()
df_map["suburb_clean"] = df_map["suburb"].str.lower().str.strip()

# Prepare dictionary for fuzzy matching
suburb_to_region = df_map.set_index("suburb_clean")["assigned_region"].to_dict()

# Match with fuzzy logic
def best_match(suburb):
    match, score, _ = process.extractOne(suburb, suburb_to_region.keys(), scorer=fuzz.ratio)
    return suburb_to_region[match] if score >= 90 else "Unknown"

# Apply matching
df_geo["assigned_region"] = df_geo["suburb_clean"].apply(best_match)

# Drop helper column
df_geo.drop(columns=["suburb_clean"], inplace=True)

# Save result
os.makedirs("output", exist_ok=True)
df_geo.to_csv(output_path, index=False)
print(f"✅ Fuzzy join complete. Output saved to: {output_path}")

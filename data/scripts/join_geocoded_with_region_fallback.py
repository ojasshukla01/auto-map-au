import pandas as pd
import os
from rapidfuzz import process, fuzz
from scipy.spatial import cKDTree
import numpy as np

# -------- File Paths --------
geo_path = "data/suburbs_geocoded.csv"
map_path = "data/sal_to_sa4_mapping_with_latlon.csv"  # <-- must include lat/lon
output_path = "output/final_output_with_geo_fallback.csv"

# -------- Load Data --------
df_geo = pd.read_csv(geo_path)
df_map = pd.read_csv(map_path)

df_geo["suburb_clean"] = df_geo["suburb"].str.lower().str.strip()
df_map["suburb_clean"] = df_map["suburb"].str.lower().str.strip()

# Map for exact and fuzzy matches
suburb_to_region = df_map.set_index("suburb_clean")["assigned_region"].to_dict()

# -------- Matching Function --------
def match_region(row):
    suburb = row["suburb_clean"]
    state = row["state"].strip().upper()

    # 1. Exact match
    if suburb in suburb_to_region:
        return suburb_to_region[suburb]

    # 2. Fuzzy match
    match, score, _ = process.extractOne(suburb, suburb_to_region.keys(), scorer=fuzz.ratio)
    if score >= 90:
        return suburb_to_region[match]

    # 3. Fallback: Regional STATE
    return f"Regional {state}"

# -------- Step 1: Basic Matching --------
df_geo["assigned_region"] = df_geo.apply(match_region, axis=1)

# -------- Step 2: Patch "Regional" using nearest lat/lon --------
df_geo_missing = df_geo[~df_geo["assigned_region"].str.contains("Regional", na=False)].copy()
df_geo_unmapped = df_geo[df_geo["assigned_region"].str.contains("Regional", na=False)].copy()

# Prepare KDTree from known region locations
mapped_coords = df_map[["latitude", "longitude"]].dropna().values
mapped_regions = df_map["assigned_region"].values
tree = cKDTree(mapped_coords)

# Get lat/lon of unmapped rows
query_coords = df_geo_unmapped[["latitude", "longitude"]].values

# Query nearest neighbors
distances, indices = tree.query(query_coords, k=1)
df_geo_unmapped["assigned_region"] = [mapped_regions[i] for i in indices]

# -------- Final Merge and Save --------
final_df = pd.concat([df_geo_missing, df_geo_unmapped])
final_df.drop(columns=["suburb_clean"], inplace=True)
os.makedirs("output", exist_ok=True)
final_df.to_csv(output_path, index=False)

print(f"✅ Final mapping saved to: {output_path}")

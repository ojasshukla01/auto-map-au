import pandas as pd
import json
import os

# -------- Configuration --------
INPUT_CSV = "data/suburbs_geocoded.csv"
REGION_JSON = "data/seo_regions_bounding_boxes.json"
OUTPUT_CSV = "output/final_output.csv"
UNMATCHED_CSV = "output/unmatched_suburbs.csv"

# -------- Load Input Files --------

# Load suburb lat/lon data
df = pd.read_csv(INPUT_CSV)

# Load bounding boxes for SEO regions
with open(REGION_JSON, "r") as f:
    region_boxes = json.load(f)

# -------- Function: Match Suburb to Region --------
def match_region(lat, lon):
    matched_regions = []

    for region in region_boxes:
        if (
            region["lat_min"] <= lat <= region["lat_max"]
            and region["lon_min"] <= lon <= region["lon_max"]
        ):
            matched_regions.append(region["region"])

    # Return most specific match (first) or "Unmapped"
    if len(matched_regions) == 1:
        return matched_regions[0]
    elif len(matched_regions) > 1:
        return ";".join(matched_regions)  # for debug; or choose one based on priority
    else:
        return "Unmapped"

# -------- Apply Matching --------
assigned_regions = []
unmatched = []

for idx, row in df.iterrows():
    try:
        lat = float(row["latitude"])
        lon = float(row["longitude"])
        region = match_region(lat, lon)
    except Exception as e:
        print(f"⚠️ Error for suburb {row['suburb']}: {e}")
        region = "Error"

    assigned_regions.append(region)

# -------- Save Output --------
df["assigned_region"] = assigned_regions
df.to_csv(OUTPUT_CSV, index=False)

# Save unmatched suburbs
unmatched_df = df[df["assigned_region"].isin(["Unmapped", "Error"])]
unmatched_df.to_csv(UNMATCHED_CSV, index=False)

print(f"✅ Region mapping complete. Output: {OUTPUT_CSV}")
print(f"🧾 Unmatched suburbs saved to: {UNMATCHED_CSV}")

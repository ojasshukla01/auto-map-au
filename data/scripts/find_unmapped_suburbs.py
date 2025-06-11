import pandas as pd

# Load final output and mapping file
df_output = pd.read_csv("output/final_output_with_geo_fallback.csv")
df_map = pd.read_csv("data/sal_to_sa4_mapping_with_latlon.csv")

# Normalize
df_output["suburb_clean"] = df_output["suburb"].str.lower().str.strip()
df_map["suburb_clean"] = df_map["suburb"].str.lower().str.strip()

# Find missing suburbs
missing_suburbs = df_output[df_output["assigned_region"].isna() | df_output["assigned_region"].isin(["", "None", "Unknown"])]
missing_suburbs = missing_suburbs[~missing_suburbs["suburb_clean"].isin(df_map["suburb_clean"])]

# Drop duplicates and save
missing_suburbs = missing_suburbs[["suburb", "state", "latitude", "longitude"]].drop_duplicates()
missing_suburbs.to_csv("data/missing_suburbs_for_mapping_patch.csv", index=False)
print("✅ Missing suburb list saved to: data/missing_suburbs_for_mapping_patch.csv")

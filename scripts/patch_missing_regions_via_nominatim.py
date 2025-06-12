import pandas as pd
import requests
import time

df = pd.read_csv("output/final_output_cleaned_by_abs.csv")

missing = df[df['final_region'].isna() | df['final_region'].astype(str).str.strip().isin(["None", "Unknown", "", "Regional"])].copy()

def reverse_geocode(lat, lon):
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "zoom": 10,
        "addressdetails": 1
    }
    headers = {"User-Agent": "AutoMapAU QA Tool"}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        return data.get("address", {}).get("state_district") or data.get("address", {}).get("county")
    except Exception as e:
        return None

patches = []
for idx, row in missing.iterrows():
    region = reverse_geocode(row['latitude'], row['longitude'])
    patches.append(region)
    print(f"{row['suburb']} ({row['latitude']}, {row['longitude']}) → {region}")
    time.sleep(1)  # Respect Nominatim rate limit

missing['patched_region'] = patches

# Apply patches to full dataset
for i, row in missing.iterrows():
    df.loc[
        (df['suburb'] == row['suburb']) &
        (df['state'] == row['state']) &
        (df['latitude'] == row['latitude']) &
        (df['longitude'] == row['longitude']),
        'final_region'
    ] = row['patched_region']

# Save the fully patched file
df.to_csv("output/final_output_fully_patched.csv", index=False)
print("✅ Saved to output/final_output_fully_patched.csv")

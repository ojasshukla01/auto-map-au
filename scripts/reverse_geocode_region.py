import pandas as pd
import requests
import os
import time

# -------- Paths --------
INPUT_CSV = "data/suburbs_geocoded.csv"
OUTPUT_CSV = "output/final_output_with_real_regions.csv"
CACHE_CSV = "cache/reverse_lookup_cache.csv"

# -------- Setup --------
os.makedirs("cache", exist_ok=True)
os.makedirs("output", exist_ok=True)

# Load input
df = pd.read_csv(INPUT_CSV)

# Load or create cache
if os.path.exists(CACHE_CSV):
    cache_df = pd.read_csv(CACHE_CSV)
else:
    cache_df = pd.DataFrame(columns=["latitude", "longitude", "county", "state_district", "state"])

# -------- Reverse Geocode Function --------
def reverse_geocode(lat, lon):
    """Call Nominatim reverse API for a lat/lon"""
    url = f"https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "jsonv2",
        "zoom": 10,
        "addressdetails": 1
    }
    headers = {
        "User-Agent": "AutoMapAU-Geocoder"
    }

    try:
        res = requests.get(url, params=params, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            addr = data.get("address", {})
            return (
                addr.get("county", "Unknown"),
                addr.get("state_district", addr.get("region", "Unknown")),
                addr.get("state", "Unknown")
            )
    except Exception as e:
        print(f"⚠️ Error for ({lat}, {lon}): {e}")
    return "Unknown", "Unknown", "Unknown"

# -------- Processing Loop --------
regions = []

for idx, row in df.iterrows():
    lat = round(float(row['latitude']), 6)
    lon = round(float(row['longitude']), 6)

    # Check cache
    cached = cache_df[(cache_df['latitude'] == lat) & (cache_df['longitude'] == lon)]
    if not cached.empty:
        county = cached.iloc[0]['county']
        district = cached.iloc[0]['state_district']
        state = cached.iloc[0]['state']
    else:
        print(f"🔍 Reverse geocoding ({lat}, {lon})...")
        county, district, state = reverse_geocode(lat, lon)
        cache_df = pd.concat([cache_df, pd.DataFrame([{
            "latitude": lat,
            "longitude": lon,
            "county": county,
            "state_district": district,
            "state": state
        }])], ignore_index=True)
        time.sleep(1.1)  # Respect rate limits

    regions.append({
        "county": county,
        "state_district": district,
        "state": state
    })

# -------- Merge & Save --------
region_df = pd.DataFrame(regions)
merged = pd.concat([df, region_df], axis=1)
merged.to_csv(OUTPUT_CSV, index=False)
cache_df.to_csv(CACHE_CSV, index=False)

print(f"✅ Region mapping complete. Output saved to {OUTPUT_CSV}")

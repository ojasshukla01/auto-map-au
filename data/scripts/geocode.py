import pandas as pd
import requests
import os
import time

# Optional: Insert your OpenCage API Key here
OPENCAGE_API_KEY = os.getenv("OPENCAGE_KEY", "6563b9e617f2421e94cef7bb926decc3")

INPUT_CSV = "data/suburbs_with_coordinates.csv"
CACHE_CSV = "cache/geocode_cache.csv"
OUTPUT_CSV = "data/suburbs_geocoded.csv"

# Ensure cache directory exists
os.makedirs("cache", exist_ok=True)

# Load input file with suburb, state, lat, lon
df = pd.read_csv(INPUT_CSV)

# Load existing cache if present
if os.path.exists(CACHE_CSV):
    cache_df = pd.read_csv(CACHE_CSV)
else:
    cache_df = pd.DataFrame(columns=["suburb", "state", "latitude", "longitude"])

# ---------- OpenCage API Geocoder ----------
def geocode_opencage(suburb, state):
    query = f"{suburb}, {state}, Australia"
    url = f"https://api.opencagedata.com/geocode/v1/json?q={query}&key={OPENCAGE_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                lat = data['results'][0]['geometry']['lat']
                lon = data['results'][0]['geometry']['lng']
                return lat, lon
    except Exception as e:
        print(f"⚠️ OpenCage error for {query}: {e}")
    return None, None

# ---------- Nominatim Fallback ----------
def geocode_nominatim(suburb, state):
    query = f"{suburb}, {state}, Australia"
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"
    headers = {"User-Agent": "AutoMapAU-Geocoder"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return lat, lon
    except Exception as e:
        print(f"⚠️ Nominatim error for {query}: {e}")
    return None, None

# ---------- Main Loop ----------
for idx, row in df.iterrows():
    if pd.isna(row['latitude']) or pd.isna(row['longitude']):
        suburb = row['suburb']
        state = row['state']

        # 1. Check if this combo exists in cache
        cached = cache_df[(cache_df['suburb'] == suburb) & (cache_df['state'] == state)]
        if not cached.empty:
            lat = cached.iloc[0]['latitude']
            lon = cached.iloc[0]['longitude']
        else:
            print(f"🌐 Geocoding: {suburb}, {state}")

            # 2. Try OpenCage first
            lat, lon = geocode_opencage(suburb, state)
            if not lat or not lon:
                print("🔁 Falling back to Nominatim...")
                lat, lon = geocode_nominatim(suburb, state)

            # 3. Append to cache
            cache_df = pd.concat([cache_df, pd.DataFrame([{
                "suburb": suburb,
                "state": state,
                "latitude": lat,
                "longitude": lon
            }])], ignore_index=True)

            # Respect API limits
            time.sleep(1.2)

        # 4. Update current dataframe
        df.at[idx, 'latitude'] = lat
        df.at[idx, 'longitude'] = lon

# ---------- Save Outputs ----------
df.to_csv(OUTPUT_CSV, index=False)
cache_df.to_csv(CACHE_CSV, index=False)
print(f"✅ Geocoding complete. Results saved to {OUTPUT_CSV}")
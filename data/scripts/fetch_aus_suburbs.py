import pandas as pd
import zipfile
import requests
import os

# Constants
GEONAMES_ZIP_URL = "http://download.geonames.org/export/zip/AU.zip"
LOCAL_ZIP_PATH = "data/AU.zip"
EXTRACTED_FILE_PATH = "data/AU.txt"
OUTPUT_CSV_PATH = "data/suburbs_with_coordinates.csv"

# Create data folder if not exists
os.makedirs("data", exist_ok=True)

# Step 1: Download zip if not exists
if not os.path.exists(LOCAL_ZIP_PATH):
    print("📥 Downloading AU.zip from Geonames...")
    response = requests.get(GEONAMES_ZIP_URL)
    with open(LOCAL_ZIP_PATH, "wb") as f:
        f.write(response.content)
    print("✅ Download complete.")

# Step 2: Unzip the file
if not os.path.exists(EXTRACTED_FILE_PATH):
    print("📦 Extracting AU.zip...")
    with zipfile.ZipFile(LOCAL_ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall("data/")
    print("✅ Extraction complete.")

# Step 3: Read and filter the data
print("📊 Processing suburb data...")

cols = [
    "country_code", "postal_code", "place_name", "admin_name1", "admin_code1",
    "admin_name2", "admin_code2", "admin_name3", "admin_code3", "latitude",
    "longitude", "accuracy"
]

df = pd.read_csv(EXTRACTED_FILE_PATH, delimiter="\t", names=cols, dtype=str)
df = df[["place_name", "admin_code1", "latitude", "longitude"]]
df.columns = ["suburb", "state", "latitude", "longitude"]
df.drop_duplicates(inplace=True)

# Step 4: Save final clean version
df.to_csv(OUTPUT_CSV_PATH, index=False)
print(f"✅ Saved full suburb dataset with coordinates: {OUTPUT_CSV_PATH}")

import pandas as pd
import argparse
import os
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.settings import COUNTRY_CONFIG

def validate_output(country_code):
    config = COUNTRY_CONFIG.get(country_code)
    if not config:
        raise ValueError(f"❌ Unsupported country code: {country_code}")

    df = pd.read_csv(config["output_file"])
    total = len(df)
    missing = df['final_region'].isna().sum()
    placeholder_values = ["Unknown", "None", "", "Regional", "Unmappable - Needs Manual Classification"]
    bad_values = df['final_region'].astype(str).str.strip().isin(placeholder_values).sum()

    lat_ok = df['latitude'].between(-90, 90).all()
    lon_ok = df['longitude'].between(-180, 180).all()

    print(f"\n🔍 QA Report for {config['name']}")
    print(f"📦 Total rows: {total}")
    print(f"✅ Mapped: {total - (missing + bad_values)}")
    print(f"🚫 Missing final_region: {missing}")
    print(f"🚫 Placeholder/Bad region values: {bad_values}")
    print(f"🌐 Coordinates valid: {lat_ok and lon_ok}")
    print("✅ QA Complete.\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cross-country QA validation")
    parser.add_argument("--country", required=True, help="Country code (au, nz, in)")
    args = parser.parse_args()
    validate_output(args.country.lower())

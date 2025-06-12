import geopandas as gpd
import pandas as pd
import os

# Path to India's shapefile
shapefile = "countries/in/boundaries/india-districts.shp"
gdf = gpd.read_file(shapefile)

# Reproject to a meter-based CRS for accurate centroids
gdf = gdf.to_crs(epsg=3857)
gdf["centroid"] = gdf.geometry.centroid
gdf = gdf.set_geometry("centroid").to_crs(epsg=4326)

# Extract required fields
df = pd.DataFrame({
    "suburb": gdf["DISTRICT"].str.strip(),
    "state": gdf["ST_NM"].str.strip(),
    "latitude": gdf.geometry.y,
    "longitude": gdf.geometry.x
})

# Save to CSV
output_path = "countries/in/source.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
df.to_csv(output_path, index=False)

print(f"✅ Saved source.csv with {len(df)} rows at {output_path}")

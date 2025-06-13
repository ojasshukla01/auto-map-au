import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import sys
import os

# ✅ Ensure config/settings.py is importable (important for Streamlit Cloud)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.settings import COUNTRY_CONFIG

# ------------------------
# PAGE CONFIG
# ------------------------

st.set_page_config(page_title="AutoMap360 Dashboard", layout="wide")
st.title("📍 AutoMap360: Suburb-to-Region Mapping Dashboard")

# ------------------------
# SIDEBAR FILTER: COUNTRY FIRST
# ------------------------

with st.sidebar:
    st.header("🌍 Select Country to Begin")
    country_display = st.selectbox("Country", ["Select Country"] + [v["name"] for v in COUNTRY_CONFIG.values()])

if country_display == "Select Country":
    st.info("Please select a country from the sidebar to load mapping data.")
    st.stop()

# Get the selected country config
country_code = next(code for code, cfg in COUNTRY_CONFIG.items() if cfg["name"] == country_display)
config = COUNTRY_CONFIG[country_code]

# ------------------------
# LOAD DATA (Only CSVs)
# ------------------------

@st.cache_data
def load_data(path):
    return pd.read_csv(path)

try:
    df = load_data(config["output_file"])
except Exception as e:
    st.error(f"❌ Could not load data for {country_display}: {e}")
    st.stop()

# ------------------------
# GLOBAL METRICS
# ------------------------

unmapped_keywords = ["Unknown", "None", "", "Regional", "Unmappable - Needs Manual Classification"]
total = len(df)
unique_regions = df['final_region'].nunique()
unmapped = df['final_region'].isna().sum() + df['final_region'].astype(str).str.strip().isin(unmapped_keywords).sum()

col1, col2, col3 = st.columns(3)
col1.metric("🧾 Total Suburbs", total)
col2.metric("🌐 Regions Assigned", unique_regions)
col3.metric("❌ Unmapped or Edge Cases", unmapped)

st.markdown("---")

# ------------------------
# SIDEBAR FILTERS
# ------------------------

with st.sidebar:
    st.header("🔎 Refine Your View")
    selected_state = st.selectbox("Select State", ["All"] + sorted(df["state"].dropna().unique().tolist()))
    selected_region = st.selectbox("Select Region", ["All"] + sorted(df["final_region"].dropna().unique().tolist()))
    selected_suburb = st.text_input("Search Suburb (partial match, case-insensitive)")

# ------------------------
# FILTER DATA
# ------------------------

filtered = df.copy()

if selected_state != "All":
    filtered = filtered[filtered["state"] == selected_state]

if selected_region != "All":
    filtered = filtered[filtered["final_region"] == selected_region]

if selected_suburb:
    filtered = filtered[filtered["suburb"].str.lower().str.contains(selected_suburb.lower())]

# ------------------------
# FILTERED METRICS
# ------------------------

st.markdown("---")
st.subheader(f"📂 Filtered Results for {country_display}")

filtered_total = len(filtered)
filtered_unmapped = (
    filtered['final_region'].isna().sum() +
    filtered['final_region'].astype(str).str.strip().isin(unmapped_keywords).sum()
)
filtered_mapped = filtered_total - filtered_unmapped
mapped_percent = (filtered_mapped / filtered_total * 100) if filtered_total > 0 else 0

colA, colB, colC, colD = st.columns(4)
colA.metric("📦 Filtered Total", filtered_total)
colB.metric("🧭 Mapped", filtered_mapped)
colC.metric("🚫 Unmapped", filtered_unmapped)
colD.metric("✅ Mapped %", f"{mapped_percent:.2f}%")

# ------------------------
# DATA TABLE
# ------------------------

st.markdown("### 📋 Filtered Suburb Data")
st.dataframe(filtered[["suburb", "state", "final_region", "latitude", "longitude"]], use_container_width=True)

# ------------------------
# MAP WITH FOLIUM
# ------------------------

MAX_MARKERS = 500
filtered_map = filtered.head(MAX_MARKERS)

if not filtered_map.empty:
    st.subheader("🗺️ Map View (Filtered)")
    avg_lat = filtered_map["latitude"].mean()
    avg_lon = filtered_map["longitude"].mean()
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=6)
    for _, row in filtered_map.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=4,
            color="blue",
            fill=True,
            fill_color="blue",
            fill_opacity=0.7,
            popup=f"{row['suburb']} ({row['state']}) → {row['final_region']}"
        ).add_to(m)
    st_data = st_folium(m, width=1000)
else:
    st.info("No suburbs to show on map.")

# ------------------------
# DOWNLOADS
# ------------------------

st.markdown("### 📥 Download Filtered Results")
st.download_button(
    label="Download CSV (Filtered)",
    data=filtered.to_csv(index=False),
    file_name=f"filtered_suburbs_{country_code}.csv",
    mime="text/csv"
)

unmapped_df = df[df['final_region'].isna() | df['final_region'].astype(str).str.strip().isin(unmapped_keywords)]
if not unmapped_df.empty:
    st.markdown("### 🚧 Export Only Unmapped or Edge Cases")
    st.download_button(
        label="Download Unmapped CSV",
        data=unmapped_df.to_csv(index=False),
        file_name=f"unmapped_suburbs_{country_code}.csv",
        mime="text/csv"
    )
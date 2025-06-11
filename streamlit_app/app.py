import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ------------------------
# CONFIG & LOAD DATA
# ------------------------

st.set_page_config(page_title="AutoMapAU Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("output/final_output_with_geo_fallback.csv")
    return df

df = load_data()

st.title("📍 AutoMapAU: Suburb-to-Region Mapping Dashboard")

# ------------------------
# METRICS
# ------------------------

total = len(df)
unique_regions = df['assigned_region'].nunique()
unmapped = df['assigned_region'].isna().sum() + (df['assigned_region'].astype(str).str.strip().isin(["Unknown", "Regional", ""])).sum()

col1, col2, col3 = st.columns(3)
col1.metric("🧾 Total Suburbs", total)
col2.metric("🌐 Regions Assigned", unique_regions)
col3.metric("❌ Unmapped", unmapped)

st.markdown("---")

# ------------------------
# SIDEBAR FILTERS
# ------------------------

with st.sidebar:
    st.header("🔎 Filters")
    region = st.selectbox("Filter by Region", options=["All"] + sorted(df['assigned_region'].dropna().unique().tolist()))
    state = st.selectbox("Filter by State", options=["All"] + sorted(df['state'].dropna().unique().tolist()))
    search = st.text_input("Search Suburb (partial match, case-insensitive)")

# ------------------------
# FILTER DATA
# ------------------------

filtered = df.copy()
if region != "All":
    filtered = filtered[filtered["assigned_region"] == region]
if state != "All":
    filtered = filtered[filtered["state"] == state]
if search:
    filtered = filtered[filtered["suburb"].str.lower().str.contains(search.lower())]

st.subheader(f"📂 Showing {len(filtered)} suburbs")

st.dataframe(filtered[["suburb", "state", "assigned_region", "latitude", "longitude"]], use_container_width=True)

# ------------------------
# MAP WITH MARKERS (LIMITED)
# ------------------------

MAX_MARKERS = 500
if len(filtered) > MAX_MARKERS:
    st.warning(f"Showing only first {MAX_MARKERS} markers for performance.")
    filtered_map = filtered.head(MAX_MARKERS)
else:
    filtered_map = filtered

if not filtered_map.empty:
    m = folium.Map(location=[-25.0, 133.0], zoom_start=4)
    for _, row in filtered_map.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=4,
            color="blue",
            fill=True,
            fill_color="blue",
            fill_opacity=0.7,
            popup=f"{row['suburb']} ({row['state']}) → {row['assigned_region']}"
        ).add_to(m)

    st.subheader("🗺️ Map of Suburbs")
    st_data = st_folium(m, width=1000)

else:
    st.info("No suburbs to show on map.")

# --- Download filtered CSV ---
st.markdown("### 📥 Export Filtered Suburbs")
st.download_button(
    label="Download CSV",
    data=filtered.to_csv(index=False),
    file_name="filtered_suburbs.csv",
    mime="text/csv"
)

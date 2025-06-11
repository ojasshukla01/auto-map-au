
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
    return pd.read_csv("output/final_output_with_geo_fallback.csv")

df = load_data()

st.title("📍 AutoMapAU: Suburb-to-Region Mapping Dashboard")

# ------------------------
# GLOBAL METRICS
# ------------------------

total = len(df)
unique_regions = df['assigned_region'].nunique()
unmapped = df['assigned_region'].isna().sum() + df['assigned_region'].astype(str).str.strip().isin(["Unknown", "Regional", "", "None"]).sum()

col1, col2, col3 = st.columns(3)
col1.metric("🧾 Total Suburbs", total)
col2.metric("🌐 Regions Assigned", unique_regions)
col3.metric("❌ Unmapped", unmapped)

st.markdown("---")

# ------------------------
# SIDEBAR FILTERS (Dependent)
# ------------------------

with st.sidebar:
    st.header("🔎 Filters")

    selected_state = st.selectbox("Select State", options=["All"] + sorted(df["state"].dropna().unique().tolist()))

    if selected_state != "All":
        state_df = df[df["state"] == selected_state]
    else:
        state_df = df.copy()

    available_regions = sorted(state_df["assigned_region"].dropna().unique().tolist())
    available_suburbs = sorted(state_df["suburb"].dropna().unique().tolist())

    selected_region = st.selectbox("Select Region", options=["All"] + available_regions)
    selected_suburb = st.text_input("Search Suburb (partial match, case-insensitive)")

# ------------------------
# FILTER DATA
# ------------------------

filtered = state_df.copy()

if selected_region != "All":
    filtered = filtered[filtered["assigned_region"] == selected_region]
if selected_suburb:
    filtered = filtered[filtered["suburb"].str.lower().str.contains(selected_suburb.lower())]

# ------------------------
# FILTER METRICS
# ------------------------

st.markdown("---")
st.subheader("📂 Filtered Suburb Summary")

filtered_total = len(filtered)
filtered_unmapped = (
    filtered['assigned_region'].isna().sum() +
    filtered['assigned_region'].astype(str).str.strip().isin(["Unknown", "Regional", "", "None"]).sum()
)
filtered_mapped = filtered_total - filtered_unmapped
mapped_percent = (filtered_mapped / filtered_total * 100) if filtered_total > 0 else 0

colA, colB, colC, colD = st.columns(4)
colA.metric("📦 Filtered Total", filtered_total)
colB.metric("🧭 Mapped", filtered_mapped)
colC.metric("🚫 Unmapped", filtered_unmapped)
colD.metric("✅ Mapped %", f"{mapped_percent:.2f}%")

# ------------------------
# TABLE PREVIEW
# ------------------------

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
    st.subheader("🗺️ Map of Suburbs")
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
    st_data = st_folium(m, width=1000)
else:
    st.info("No suburbs to show on map.")

# ------------------------
# DOWNLOAD BUTTON
# ------------------------

st.markdown("### 📥 Export Filtered Suburbs")
st.download_button(
    label="Download CSV",
    data=filtered.to_csv(index=False),
    file_name="filtered_suburbs.csv",
    mime="text/csv"
)

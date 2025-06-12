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
    return pd.read_csv("output/final_output_fully_patched.csv")

df = load_data()

st.title("📍 AutoMapAU: Suburb-to-Region Mapping Dashboard")

# ------------------------
# GLOBAL METRICS
# ------------------------

total = len(df)
unique_regions = df['final_region'].nunique()
unmapped_keywords = ["Unknown", "None", "", "Regional", "Unmappable - Needs Manual Classification"]
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
    st.header("🔎 Filters")

    selected_state = st.selectbox("Select State", options=["All"] + sorted(df["state"].dropna().unique().tolist()))

    state_df = df.copy() if selected_state == "All" else df[df["state"] == selected_state]

    available_regions = sorted(state_df["final_region"].dropna().unique().tolist())
    available_suburbs = sorted(state_df["suburb"].dropna().unique().tolist())

    selected_region = st.selectbox("Select Region", options=["All"] + available_regions)
    selected_suburb = st.text_input("Search Suburb (partial match, case-insensitive)")

# ------------------------
# FILTER DATA
# ------------------------

filtered = state_df.copy()

if selected_region != "All":
    filtered = filtered[filtered["final_region"] == selected_region]
if selected_suburb:
    filtered = filtered[filtered["suburb"].str.lower().str.contains(selected_suburb.lower())]

# ------------------------
# FILTER METRICS
# ------------------------

st.markdown("---")
st.subheader("📂 Filtered Suburb Summary")

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
# TABLE PREVIEW
# ------------------------

st.dataframe(filtered[["suburb", "state", "final_region", "latitude", "longitude"]], use_container_width=True)

# ------------------------
# MAP WITH MARKERS
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
            popup=f"{row['suburb']} ({row['state']}) → {row['final_region']}"
        ).add_to(m)
    st_data = st_folium(m, width=1000)
else:
    st.info("No suburbs to show on map.")

# ------------------------
# DOWNLOAD BUTTONS
# ------------------------

st.markdown("### 📥 Download Filtered Results")
st.download_button(
    label="Download CSV (Filtered)",
    data=filtered.to_csv(index=False),
    file_name="filtered_suburbs.csv",
    mime="text/csv"
)

# Optional: Download unmapped
unmapped_df = df[df['final_region'].isna() | df['final_region'].astype(str).str.strip().isin(unmapped_keywords)]
if not unmapped_df.empty:
    st.markdown("### 🚧 Export Only Unmapped or Edge Cases")
    st.download_button(
        label="Download Unmapped CSV",
        data=unmapped_df.to_csv(index=False),
        file_name="unmapped_or_edge_suburbs.csv",
        mime="text/csv"
    )

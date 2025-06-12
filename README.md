# 🗺️ AutoMap360: Global Suburb-to-Region Mapping Engine (AU, NZ, IN)

AutoMap360 is a full-stack, open-source geospatial pipeline that maps suburb/locality-level data to standardized regions using government-backed shapefiles. It supports Australia 🇦🇺, New Zealand 🇳🇿, and India 🇮🇳 with region assignment, QA checks, and a Streamlit dashboard.

---

## 🎯 Project Vision

To empower developers and data teams with a transparent, extensible, and fully free solution for geospatial grouping using authoritative public data – no API fees, no manual mapping.

### Why AutoMap360?
- ✅ **100% offline + reproducible**
- 📍 **Accurate**: Uses official SA4 (AU), district (IN), and territorial/local authority (NZ) boundaries
- 🧠 **Intelligent**: Uses spatial joins, fuzzy matching, geocoding, and QA
- 🧪 **Auditable**: QA reports on mapping accuracy, unmapped cases, and confidence
- 🔄 **Reusable**: Modular scripts for ingestion, validation, patching

---

## 🌐 Supported Countries

| Country       | Region Field     | Coverage         | Input Source Format |
|---------------|------------------|------------------|----------------------|
| Australia 🇦🇺  | SA4_NAME21       | 17,732 suburbs   | Cleaned CSV          |
| New Zealand 🇳🇿| name (GeoJSON)   | 6,562 suburbs    | Shape → CSV          |
| India 🇮🇳      | DISTRICT         | 641 districts    | Census shapefile     |

---

## 🧰 Tech Stack

- `Python 3.10+`
- `pandas`, `numpy`, `geopandas`
- `RapidFuzz`, `SciPy`, `shapely`
- `streamlit`, `folium`

---

## 📁 Folder Structure

```
auto-map-au/
├── countries/
│   ├── au/
│   │   ├── source.csv
│   │   └── boundaries/ (excluded from GitHub)
│   ├── nz/
│   ├── in/
├── output/
├── scripts/
├── qa_logs/
├── streamlit_app/
│   └── app.py
├── config/
│   └── settings.py
└── requirements.txt
```

---

## 🚀 How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run pipeline for a country (au, nz, in)
python scripts/pipeline.py --country au

# 3. QA report (optional)
python scripts/validate_mapping.py --country au

# 4. Launch dashboard
streamlit run streamlit_app/app.py
```

---

## 🗃️ Shapefile Setup (Required!)

Due to GitHub limits, boundary files are excluded. Download and place them in:

- **Australia**: `countries/au/boundaries/SA4_2021_AUST_GDA2020.shp` (from ABS)
- **New Zealand**: `countries/nz/boundaries/nz-suburbs-and-localities.shp` (from LINZ LDS)
- **India**: `countries/in/boundaries/india-districts.shp` (from Datameet or Bhuvan)

---

## 📊 Dashboard Features

- Search, filter, and view suburbs by country/state/region
- Interactive folium map with markers and popups
- Download buttons for filtered/unmapped exports

---

## 📦 Outputs

| File                          | Description                    |
|-------------------------------|--------------------------------|
| `output.csv`                 | Final mapping per country      |
| `qa_logs/qa_summary.txt`     | QA metrics                     |
| `qa_logs/unmapped.csv`       | Suburbs with missing regions   |

---

## 🧑‍💻 Author

**Ojas Shukla**  
Data Engineer | Open Geo Advocate | OSS Contributor  
[GitHub](https://github.com/ojasshukla01) | [LinkedIn](https://linkedin.com/in/ojas-shukla)

---

## 📘 License

MIT License – Free to use, modify, and build on.
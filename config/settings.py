COUNTRY_CONFIG = {
    "au": {
        "name": "Australia",
        "input_file": "countries/au/final_output_fully_patched.csv",
        "boundary_file": "countries/au/boundaries/SA4_2021_AUST_GDA2020.shp",
        "output_file": "countries/au/output.csv"
    },
    "nz": {
        "name": "New Zealand",
        "input_file": "countries/nz/source.csv",
        "output_file": "countries/nz/output.csv",
        "boundary_file": "countries/nz/boundaries/nz-suburbs-and-localities.shp",
        "region_field": "territoria"
    },
    "in": {
        "name": "India",
        "input_file": "countries/in/source.csv",
        "output_file": "countries/in/output.csv",
        "boundary_file": "countries/in/boundaries/india-districts.shp",
        "region_field": "DISTRICT"
    }
}

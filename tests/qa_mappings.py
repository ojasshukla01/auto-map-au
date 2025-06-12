
# tests/qa_mappings.py

import pandas as pd

def test_no_unmapped_regions():
    df = pd.read_csv('output/final_output_cleaned_by_abs.csv')
    assert df['final_region'].notna().all(), "There are still unmapped (null) final regions!"

def test_valid_coordinates():
    df = pd.read_csv('output/final_output_cleaned_by_abs.csv')
    assert df['latitude'].between(-44, -10).all(), "Some latitudes are out of bounds for Australia"
    assert df['longitude'].between(110, 155).all(), "Some longitudes are out of bounds for Australia"

def test_region_correction_logged():
    df = pd.read_csv('output/final_output_cleaned_by_abs.csv')
    changed = df['was_different'].sum()
    total = len(df)
    print(f"{changed} out of {total} suburbs had corrected regions.")
    assert changed > 0, "No regions were corrected — check if patching logic was applied"

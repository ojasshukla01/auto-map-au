import pandas as pd
import os
import random

# --------- Config ---------
INPUT_FILE = "output/final_output_with_regions.csv"
SUMMARY_FILE = "qa_logs/qa_summary.txt"
UNMAPPED_FILE = "qa_logs/unmapped_suburbs.csv"
SAMPLE_FILE = "qa_logs/sample_check.csv"

# Ensure output folder exists
os.makedirs("qa_logs", exist_ok=True)

# --------- Load Data ---------
df = pd.read_csv(INPUT_FILE)

# --------- Basic Stats ---------
total_rows = len(df)
missing_region = df["assigned_region"].isna().sum()
unique_regions = df["assigned_region"].nunique(dropna=True)
top_regions = df["assigned_region"].value_counts().head(5)

# --------- Sample Check ---------
sample_df = df.sample(n=100, random_state=42)
sample_df.to_csv(SAMPLE_FILE, index=False)

# --------- Unmapped Suburbs ---------
unmapped_df = df[df["assigned_region"].isna()]
unmapped_df.to_csv(UNMAPPED_FILE, index=False)

# --------- Save Summary ---------
with open(SUMMARY_FILE, "w") as f:
    f.write(f"QA SUMMARY\n")
    f.write(f"------------------------\n")
    f.write(f"Total suburbs: {total_rows}\n")
    f.write(f"Unmapped suburbs: {missing_region}\n")
    f.write(f"Unique regions assigned: {unique_regions}\n\n")
    f.write("Top 5 regions:\n")
    f.write(top_regions.to_string())
    f.write("\n\nSample of 100 records written to sample_check.csv\n")
    f.write("Unmapped records written to unmapped_suburbs.csv\n")

print(f"✅ QA summary saved to: {SUMMARY_FILE}")

import os
import pandas as pd
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

# Paths for the ANAFORES data
BASE_DIR = os.path.join(PROJECT_ROOT, "data", "ANAFORES")
# Output location for the isolated CSV
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "stats", "fit39_daily_2020_2025.csv")

YEARS = range(2020, 2026)
SHEET_NAME = "ΠΑΡΟΧΗ"  # The "Flow" sheet in the XLS files

def extract_fit39():
    """Extracts only FIT 3.9 daily data from 2020 to 2025."""
    all_rows = []

    print(f"🚀 Starting extraction of FIT 3.9 from {BASE_DIR}...")

    for year in YEARS:
        folder = os.path.join(BASE_DIR, f"STATISTIKA_ETOYS_{year}")
        if not os.path.exists(folder):
            print(f"  ⚠️ Skipping {year}: Folder not found.")
            continue

        for month in range(1, 13):
            filename = f"MONTH_{month}_{year}.xls"
            filepath = os.path.join(folder, filename)
            
            if not os.path.exists(filepath):
                continue

            try:
                # Read the flow sheet
                df = pd.read_excel(filepath, sheet_name=SHEET_NAME)
                
                # Identify the Date and FIT 3.9 columns
                # We look for "HM/NIA" for date and "FIT" + "3.9" for the flow
                date_col = None
                fit39_col = None

                for col in df.columns:
                    col_str = str(col).upper()
                    if "HM/NIA" in col_str:
                        date_col = col
                    if "FIT" in col_str and "3.9" in col_str:
                        fit39_col = col

                if date_col and fit39_col:
                    # Keep only relevant columns and drop rows with empty dates
                    temp_df = df[[date_col, fit39_col]].copy()
                    temp_df.columns = ["date", "fit_3_9_flow_m3"]
                    
                    # Convert date and clean numeric values
                    temp_df["date"] = pd.to_datetime(temp_df["date"], format="%d/%m/%Y", errors="coerce")
                    temp_df.dropna(subset=["date"], inplace=True)
                    temp_df["fit_3_9_flow_m3"] = pd.to_numeric(temp_df["fit_3_9_flow_m3"], errors="coerce").fillna(0)
                    
                    all_rows.append(temp_df)
                    print(f"  ✅ {filename}: Processed {len(temp_df)} rows.")
                else:
                    print(f"  ❌ {filename}: Could not find both 'Date' and 'FIT 3.9' columns.")
            
            except Exception as e:
                print(f"  💥 ERROR processing {filename}: {e}")

    if not all_rows:
        print("❌ No data was found. Please check your file paths and names.")
        return

    # Combine all months/years
    final_df = pd.concat(all_rows, ignore_index=True)
    final_df.sort_values("date", inplace=True)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    
    # Save to CSV
    final_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"\n✨ Success! Isolated CSV saved to: {OUTPUT_PATH}")
    print(f"📊 Total records collected: {len(final_df)}")

if __name__ == "__main__":
    extract_fit39()

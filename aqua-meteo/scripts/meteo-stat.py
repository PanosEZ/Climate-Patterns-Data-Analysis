import os
import pandas as pd
from functools import reduce

# ============================================================
# CONFIGURATION
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

# Inputs
WEATHER_BASE_DIR = os.path.join(PROJECT_ROOT, "data", "openmeteo", "station")

# Outputs
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "stats")

# The stations and metrics we want to process
STATIONS = ["kampi", "kompoti"]
METRICS = ["temperature", "humidity", "rainfall"]

def clean_and_export():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for station in STATIONS:
        print(f"Processing 10-minute data for station: {station.upper()}...")
        
        station_dataframes = []
        
        for metric in METRICS:
            filename = f"{metric}-{station}.csv"
            filepath = os.path.join(WEATHER_BASE_DIR, f"station-{station}", filename)
            
            if not os.path.exists(filepath):
                print(f"  Skipping {metric}: File not found at {filepath}")
                continue
                
            try:
                # 1. Read the CSV without headers, grabbing only the first 2 columns
                df = pd.read_csv(filepath, header=None, usecols=[0, 1])
            except Exception as e:
                print(f"  Error reading {filename}: {e}")
                continue
            
            # 2. Force clean headers
            df.columns = ["date", metric]
            
            # 3. Convert to datetime
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df.dropna(subset=["date"], inplace=True)
            
            # 4. Strip the time off (e.g., 2021-04-15 14:20 becomes 2021-04-15)
            df["date"] = df["date"].dt.normalize()
            
            # Ensure the metric is a number, not a string
            df[metric] = pd.to_numeric(df[metric], errors="coerce")
            
            # 5. AGGREGATE TO DAILY
            print(f"  Aggregating {metric} to daily...")
            if metric == "rainfall":
                # Rain gets SUMMED for the day
                df_daily = df.groupby("date", as_index=False)[metric].sum()
            else:
                # Temp and Humidity get AVERAGED for the day
                df_daily = df.groupby("date", as_index=False)[metric].mean()
                
            # Round to 2 decimal places to keep the final CSV looking clean
            df_daily[metric] = df_daily[metric].round(2)
            
            station_dataframes.append(df_daily)
            
        # 6. Merge all three metrics into a single Daily DataFrame
        if len(station_dataframes) == 3:
            final_station_df = reduce(lambda left, right: pd.merge(left, right, on="date", how="outer"), station_dataframes)
            
            final_station_df.sort_values("date", inplace=True)
            
            # Save to CSV using the requested naming format
            output_filepath = os.path.join(OUTPUT_DIR, f"stat_{station}.csv")
            final_station_df.to_csv(output_filepath, index=False, encoding="utf-8-sig")
            
            print(f"SUCCESS! Saved clean data to: {output_filepath}")
            print("-" * 60)
        else:
            print(f"Failed to process all metrics for {station}. Could not generate final CSV.")
            print("-" * 60)

if __name__ == "__main__":
    clean_and_export()
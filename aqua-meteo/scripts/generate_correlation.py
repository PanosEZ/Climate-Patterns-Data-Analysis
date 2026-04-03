import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# ============================================================
# CONFIGURATION
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
STATS_DIR = os.path.join(PROJECT_ROOT, "stats")

# Input Files
FIT39_CSV = os.path.join(STATS_DIR, "fit39_daily_2020_2025.csv")
KAMPI_CSV = os.path.join(STATS_DIR, "stat_kampi.csv")
KOMPOTI_CSV = os.path.join(STATS_DIR, "stat_kompoti.csv")

# Output Files
MATRIX_CSV_OUTPUT = os.path.join(STATS_DIR, "matrix_weight_table.csv")
HEATMAP_IMG_OUTPUT = os.path.join(STATS_DIR, "correlation_heatmap.png")

def generate_matrix():
    print("Loading data files...")
    
    # 1. Load the data, ensuring 'date' is a proper datetime object
    try:
        df_fit = pd.read_csv(FIT39_CSV, parse_dates=["date"])
        df_kampi = pd.read_csv(KAMPI_CSV, parse_dates=["date"])
        df_kompoti = pd.read_csv(KOMPOTI_CSV, parse_dates=["date"])
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        print("Make sure extract_fit39_daily.py and meteo-stat.py have been run first.")
        return

    # 2. Rename columns so we know which weather station is which
    df_kampi = df_kampi.rename(columns={
        "temperature": "temp_kampi",
        "humidity": "hum_kampi",
        "rainfall": "rain_kampi"
    })
    
    df_kompoti = df_kompoti.rename(columns={
        "temperature": "temp_kompoti",
        "humidity": "hum_kompoti",
        "rainfall": "rain_kompoti"
    })

    # 3. Merge everything into one Master DataFrame based on the Date
    print("Merging data sets...")
    df_master = pd.merge(df_fit, df_kampi, on="date", how="inner")
    df_master = pd.merge(df_master, df_kompoti, on="date", how="inner")
    
    # Sort by date chronologically
    df_master.sort_values("date", inplace=True)

    # 4. Add the "Lagged" variables
    print("Calculating time-lagged variables (yesterday's weather)...")
    df_master["rain_kampi_yesterday"] = df_master["rain_kampi"].shift(1)
    df_master["rain_kompoti_yesterday"] = df_master["rain_kompoti"].shift(1)
    
    # Drop the first row since "yesterday" will be blank (NaN) for the very first day
    df_master.dropna(inplace=True)

    # 5. Generate the Correlation Matrix (The "Matrix Weight Table")
    print("Calculating Matrix Weights...")
    corr_matrix = df_master.drop(columns=["date"]).corr(numeric_only=True)

    # Save the raw matrix table to CSV
    corr_matrix.to_csv(MATRIX_CSV_OUTPUT)
    print(f"Matrix Weight Table saved to: {MATRIX_CSV_OUTPUT}")

    # 6. Generate the Heatmap Image
    print("Generating Heatmap visualization...")
    plt.figure(figsize=(12, 10))
    
    # Create a mask so we only show the bottom triangle
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    
    # Paint the heatmap
    sns.heatmap(
        corr_matrix, 
        mask=mask,
        annot=True,              
        cmap="coolwarm",         
        fmt=".2f",               
        vmin=-1, vmax=1,         
        linewidths=0.5,
        cbar_kws={"shrink": .8}
    )
    
    plt.title("Matrix Weight Table - FIT 3.9 Water Flow vs. Weather", fontsize=16, pad=20)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save Image
    plt.savefig(HEATMAP_IMG_OUTPUT, dpi=300)
    plt.close()
    
    print(f"Success! Heatmap image saved to: {HEATMAP_IMG_OUTPUT}")

if __name__ == "__main__":
    generate_matrix()
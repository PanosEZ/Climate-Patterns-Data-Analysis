import pandas as pd
import json
import os
import math

base_dir = r"c:\Users\User\Desktop\aqua-dev\aqua-meteo\stats"
fit_file = os.path.join(base_dir, "fit39_daily_2020_2025.csv")
st_kampi = os.path.join(base_dir, "stat_kampi.csv")
st_kompoti = os.path.join(base_dir, "stat_kompoti.csv")
st_kostakioi = os.path.join(base_dir, "stat_kostakioi.csv")
out_js = os.path.join(base_dir, "flow_weather_data.js")

# Load and prepare data
df_fit = pd.read_csv(fit_file)
df_fit['date'] = pd.to_datetime(df_fit['date'])

df_kampi = pd.read_csv(st_kampi)
df_kompoti = pd.read_csv(st_kompoti)
df_kostakioi = pd.read_csv(st_kostakioi)

for df_iter in [df_kampi, df_kompoti, df_kostakioi]:
    df_iter['date'] = pd.to_datetime(df_iter['date'])

# Grouping weather directly (regional average of 3 stations)
df_w = pd.concat([df_kampi, df_kompoti, df_kostakioi])
df_w = df_w.groupby('date').agg({'temperature': 'mean', 'rainfall': 'mean'}).reset_index()

# Merge fit39 flow with weather
df = df_fit.merge(df_w, on='date', how='inner')
df = df.sort_values('date').set_index('date')

# Resample to make sure we have continuous days for accurate rolling operation
df = df.resample('D').asfreq()
df = df.round(1)

# --- Prepare Output Data ---
output_data = {
    'daily_raw': {
        'dates': [str(x.date()) for x in df.index],
        'flow': df['fit_3_9_flow_m3'].tolist(),
        'rainfall': df['rainfall'].tolist(),
        'temperature': df['temperature'].tolist()
    },
    'views': {}
}

for d in [1, 3, 10]:
    # Weather is the rolling sum/mean of the *previous* d days.
    temp_prev = df['temperature'].shift(1).rolling(window=d).mean()
    rain_prev = df['rainfall'].shift(1).rolling(window=d).sum()
    flow_curr = df['fit_3_9_flow_m3']
    
    view_df = pd.DataFrame({
        'flow': flow_curr,
        'rain_sum': rain_prev,
        'temp_avg': temp_prev
    }).dropna()
    
    # --- RAINFALL ANALYSIS ---
    # Categorize rain into buckets for the summary chart
    rain_bins = [-1, 0.1, 10, 30, 1000]
    rain_labels = ['Dry', 'Light', 'Medium', 'Heavy']
    view_df['rain_cat'] = pd.cut(view_df['rain_sum'], bins=rain_bins, labels=rain_labels)
    rain_grp = view_df.groupby('rain_cat', observed=False)['flow']
    rain_summary = {
        'mean': rain_grp.mean().fillna(0).round(1).to_dict(),
        'min': rain_grp.min().fillna(0).round(1).to_dict(),
        'max': rain_grp.max().fillna(0).round(1).to_dict(),
        'median': rain_grp.median().fillna(0).round(1).to_dict(),
        'count': rain_grp.count().fillna(0).astype(int).to_dict()
    }
    
    # Find matching rain events: days where it rained for d consecutive days (each day > 1mm)
    is_rainy = df['rainfall'] > 1.0
    consecutive_rain = is_rainy.rolling(window=d).sum() == d
    rain_event_days = df.index[consecutive_rain.shift(1) == True].tolist()
    
    # --- TEMPERATURE ANALYSIS ---
    # Categorize temperature into buckets
    temp_bins = [-50, 10, 18, 25, 100]
    temp_labels = ['Cold', 'Cool', 'Warm', 'Hot']
    view_df['temp_cat'] = pd.cut(view_df['temp_avg'], bins=temp_bins, labels=temp_labels)
    temp_grp = view_df.groupby('temp_cat', observed=False)['flow']
    temp_summary = {
        'mean': temp_grp.mean().fillna(0).round(1).to_dict(),
        'min': temp_grp.min().fillna(0).round(1).to_dict(),
        'max': temp_grp.max().fillna(0).round(1).to_dict(),
        'median': temp_grp.median().fillna(0).round(1).to_dict(),
        'count': temp_grp.count().fillna(0).astype(int).to_dict()
    }
    
    # Find matching temp events: days where temperature was high (>25°C) for d consecutive days
    is_hot = df['temperature'] > 25.0
    consecutive_hot = is_hot.rolling(window=d).sum() == d
    hot_event_days = df.index[consecutive_hot.shift(1) == True].tolist()
    
    output_data['views'][f"{d}d"] = {
        'rain': {
            'summary': rain_summary,
            'events': [str(x.date()) for x in rain_event_days]
        },
        'temp': {
            'summary': temp_summary,
            'events': [str(x.date()) for x in hot_event_days]
        }
    }

# Save to JS file so it can be trivially loaded locally without CORS HTTP servers
with open(out_js, "w", encoding="utf-8") as f:
    f.write("const flowWeatherData = ")
    json.dump(output_data, f, ensure_ascii=False)
    f.write(";")

print(f"Interactive data processed completely and saved to:\n{out_js}")
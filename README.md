# Aqua Water Management System

## Overview
The **Aqua System** repository encompasses a comprehensive water management, meteorological data processing, and statistical visualization suite. It contains two main interconnected sub-projects: `aqua-meteo` and `aqua-stat`. They work together to parse raw water flow metrics from pumping stations, correlate them with local weather conditions, and visualize operational trends and seasonal behaviours through a modern web dashboard.

## Project Structure

The project is broken into two primary modules:

### 1. Aqua Meteo (`aqua-meteo/`)
A Python-based data processing module focusing on metric extraction and weather-flow correlations.
- **Core Processing**: Contains data engineering scripts (e.g., `extract_fit39_daily.py`, `process_anafores.py`) that parse operational station reports.
- **Weather Analysis**: Utilizes `generate_flow_weather_plots.py` and `generate_correlation.py` to examine meteorological conditions—such as average rainfall and temperature from surrounding regional stations like Kampi, Kompoti, and Kostakioi. It maps these conditions to the water outflow (e.g., FIT 3.9) across shifting timespans (1-day, 3-day, and 10-day rolling windows) to predict flow based on weather patterns.
- **Data Generation**: Refines raw metrics into consolidated `csv` logs and lightweight static `json/js` formats designed to independently run without complex backend HTTP servers.

### 2. Visual Dashboards (HTML Frontends)
The project ships with two distinct client-side web applications (HTML dashboards) dedicated to presenting different aspects of the analysis:

- **Aqua Stat Dashboard** (`aqua-stat/index.html`): 
  - An overarching operational dashboard styled via **Tailwind CSS** and charted using **Chart.js**.
  - Offers a real-time-like overview of total water volume distributed (FIT 3.9), system energy consumption, specific energy, and active pump hours. 
  - Contains **Deep-Dive Views** for the **Kostakioi Analysis** (analyzing discrepancies between station inflow metrics and distributed outflows) and **Trend Visualisations** (annual, seasonal, and monthly system trends).

- **Flow-Weather Correlation Dashboard** (`aqua-meteo/stats/flow_weather_viewer.html`):
  - A specialized dashboard utilizing **ECharts** for visualizing meteorological impact on water flow.
  - Allows observing isolated periods (1-day, 3-day, 10-day rolling windows) of rainfall or high temperatures, cross-referencing these continuous metrics with the distribution performance (FIT 3.9 outflow).

## Getting Started

### Prerequisites
- Standard Python 3.x for running backend scripts.
- Modern web browser for the dashboard front-ends.

### Running the Dashboards
Since the web applications source dynamically generated files locally, you can serve the project via a local python static web server to avoid CORS issues from the root directory:
```bash
python -m http.server 8000
```
Then navigate to:
- **Operational Dashboard**: `http://localhost:8000/aqua-stat/index.html`
- **Weather Correlation Viewer**: `http://localhost:8000/aqua-meteo/stats/flow_weather_viewer.html`

### Data Updates
To update the datasets before displaying them on the dashboard, run the extraction scripts inside the `aqua-meteo/scripts/` directory to fetch the latest pump/meteo data and write updated statistics back into the `stats/` directories.

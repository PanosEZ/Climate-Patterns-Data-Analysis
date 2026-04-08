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

### 2. Aqua Stat Dashboard (`aqua-stat/`)
An interactive, client-side web application dedicated to presenting the insights gathered by the meteo analyses.
- **Technology Stack**: A vanilla HTML frontend styled via **Tailwind CSS** and richly charted using **Chart.js**. 
- **Main Dashboard**: Offers a real-time-like operational overview of total water volume distributed (FIT 3.9), system energy consumption, specific energy, and active pump hours. 
- **Deep-Dive Views**: 
   - **Kostakioi Analysis**: Analyzes discrepancies and absolute differences between station inflow metrics and distributed outflows.
   - **Trend Visualisations**: Contains dynamic time-selector controls allowing drill-down views of annual, seasonal, and monthly system trends—making it highly relevant for long-term performance auditing and maintenance scheduling.

## Getting Started

### Prerequisites
- Standard Python 3.x for running backend scripts.
- Modern web browser for the dashboard front-end.

### Running the Dashboard
Since the web application sources dynamically generated files locally, you can serve it via a local python static web server to avoid CORS issues:
```bash
cd aqua-stat
python -m http.server 8000
```
Then navigate to `http://localhost:8000` in your web browser.

### Data Updates
To update the datasets before displaying them on the dashboard, run the extraction scripts inside the `aqua-meteo/scripts/` directory to fetch the latest pump/meteo data and write updated statistics back into the `stats/` directories.

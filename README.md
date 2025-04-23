# IA626_SagarBangera_Spring2025
NYC 311 Complaints & Weather Analysis,


This project focuses on uncovering patterns in NYC 311 complaints with respect to time, location, and weather (temperature), using data engineering, database management, API integration, and data visualization techniques.

---

##  Project Summary

We merged two datasets:

1. **NYC 311 Complaints Dataset (2015)** - historical data of complaints from NYC residents.
2. **Custom Weather API** - provides hourly weather information by borough and date.

By combining complaints data with weather data, the goal was to analyze how temperature and time of day affect the types and volume of complaints in NYC.

---

##  Data Sources

### 1. NYC 311 Complaint Dataset
- Raw CSV file for the year 2015.
- Cleaned and preprocessed to extract fields: `date`, `hour`, `borough`, `complaint_type`, `descriptor`, `location_type`.
- Merged with weather data to include the `temperature_C` column.

### 2. Custom Weather API
- URL: [https://apps.clarksonmsda.org/](https://apps.clarksonmsda.org/)
- Python-based requests using date, hour, and borough to pull hourly temperature.
- Weather data stored in a local file: `nyc_weather_cleaned.csv`
- Supporting code: [https://github.com/whysoserious-joker/weather_api](https://github.com/whysoserious-joker/weather_api)

---

##  Code Organization

### `test1.py`
- Initial merging attempt between complaints data and raw weather data.
- Highlighted format mismatches in date/hour between datasets.

### `test2.py`
- Refined date and hour extraction.
- Better format alignment between datasets.

### `test3.py`
- Final working code to merge complaints with temperature.
- Saved output to `merged_complaints_weather.csv`
- Logged skipped rows for diagnostics.

### `test4.ipynb`
- Loads data into phymyadmin sql.

### `test5.py` *(Main Flask App)*
- Contains all Flask endpoints and visual rendering logic.
- Reads database config from `config.yaml`
- Endpoints include:
  - `/getHourlyComplaints`: JSON data of complaints by hour and borough
  - `/graph`: Bar chart view of hourly complaints
  - `/dateRangeInput`: HTML form to select start and end date
  - `/dateRangeData`: JSON and bar chart output of complaints in selected range
  - `/dateHourData`: Visualization and JSON based on hour + date filtering
  - `/nightDayPatterns`: Day vs night complaint distribution
  - `/topComplaintTypesByTemp`: Top complaint types bucketed by temperature
  - `/tempPatternInput`: Interactive selection for complaint vs temp range visualization

---

##  Configuration

A `config.yaml` file is used for secure database connection settings:

All scripts using a database call read from this file via `yaml.safe_load()`.

---

##  How to Run

1. Install dependencies:
```bash
pip install flask pymysql matplotlib pyyaml
```

2. Ensure you have the `config.yaml` file in the same directory.

3. Launch Flask app:
```bash
python test5.py
```

4. Open your browser:
```
http://127.0.0.1:5000
```

---

##  Features

- Interactive web dashboard using Flask and Chart.js
- JSON endpoints for programmatic access
- Real-time analytics filtered by date, hour, borough, and temperature
- Secure configuration via YAML
- Visualizations of complaint trends by temp, borough, time

---


#  Flask Routes Documentation

This document explains all the Flask routes exposed by the NYC 311 Complaints & Weather Analysis app.

---

## `/` – Home Page
- **Type**: HTML  
- **Description**: Welcome page with links to the JSON data and graph view.  
- **Sample Link**: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## `/getHourlyComplaints?key=123`
- **Type**: JSON  
- **Description**: Returns complaint counts grouped by hour and borough.  
- **Query Param**: `key` – API key (required)  
- **Sample Link**: [http://127.0.0.1:5000/getHourlyComplaints?key=123](http://127.0.0.1:5000/getHourlyComplaints?key=123)

---

## `/graph`
- **Type**: HTML (Graph)  
- **Description**: Bar chart showing hourly complaints for all boroughs.  
- **Sample Link**: [http://127.0.0.1:5000/graph](http://127.0.0.1:5000/graph)

---

## `/hourlyInput`
- **Type**: HTML (Form)  
- **Description**: User input for selecting hour to visualize complaints.  
- **Sample Link**: [http://127.0.0.1:5000/hourlyInput](http://127.0.0.1:5000/hourlyInput)

---

## `/hourlyData?hour=09`
- **Type**: HTML (Graph)  
- **Description**: Bar chart of complaints per borough at a given hour.  
- **Query Param**: `hour` (0–23)  
- **Sample Link**: [http://127.0.0.1:5000/hourlyData?hour=09](http://127.0.0.1:5000/hourlyData?hour=09)

---

## `/dateRangeInput`
- **Type**: HTML (Form)  
- **Description**: Form to select start and end dates for borough complaints.  
- **Sample Link**: [http://127.0.0.1:5000/dateRangeInput](http://127.0.0.1:5000/dateRangeInput)

---

## `/dateRangeData?key=123&start=2015-06-01&end=2015-06-30`
- **Type**: HTML (Graph)  
- **Description**: Graph of total complaints per borough in selected date range.  
- **Query Params**: `key`, `start`, `end`  
- **Sample Link**: [http://127.0.0.1:5000/dateRangeData?key=123&start=2015-06-01&end=2015-06-30](http://127.0.0.1:5000/dateRangeData?key=123&start=2015-06-01&end=2015-06-30)

---

## `/dateHourInput`
- **Type**: HTML (Form)  
- **Description**: Form to input both date and hour ranges.  
- **Sample Link**: [http://127.0.0.1:5000/dateHourInput](http://127.0.0.1:5000/dateHourInput)

---

## `/dateHourData?start=2015-03-01&end=2015-03-01&start_hr=5&end_hr=3&key=123`
- **Type**: HTML (Graph)  
- **Description**: Complaints over date and hour range, wraps around midnight if needed.  
- **Query Params**: `start`, `end`, `start_hr`, `end_hr`, `key`  
- **Sample Link**: [http://127.0.0.1:5000/dateHourData?start=2015-03-01&end=2015-03-01&start_hr=5&end_hr=3&key=123](http://127.0.0.1:5000/dateHourData?start=2015-03-01&end=2015-03-01&start_hr=5&end_hr=3&key=123)

---

## `/topComplaintsByTime?key=123&bucket=night`
- **Type**: HTML (Graph)  
- **Description**: Top 3 complaint types per borough for a specific time bucket (night/morning/afternoon/evening).  
- **Query Params**: `key`, `bucket`  
- **Sample Link**: [http://127.0.0.1:5000/topComplaintsByTime?key=123&bucket=night](http://127.0.0.1:5000/topComplaintsByTime?key=123&bucket=night)

---

## `/complaintsByTempBucket?key=123`
- **Type**: JSON  
- **Description**: Complaint counts grouped by temperature bucket.  
- **Sample Link**: [http://127.0.0.1:5000/complaintsByTempBucket?key=123](http://127.0.0.1:5000/complaintsByTempBucket?key=123)

---

## `/topComplaintTypesByTemp?key=123`
- **Type**: JSON  
- **Description**: Top complaint types listed per temperature range bucket.  
- **Sample Link**: [http://127.0.0.1:5000/topComplaintTypesByTemp?key=123](http://127.0.0.1:5000/topComplaintTypesByTemp?key=123)

---

## `/boroughComplaintsByTemp?key=123`
- **Type**: JSON  
- **Description**: Complaints per borough per temperature range.  
- **Sample Link**: [http://127.0.0.1:5000/boroughComplaintsByTemp?key=123](http://127.0.0.1:5000/boroughComplaintsByTemp?key=123)

---

## `/tempComplaintVisualizer`
- **Type**: HTML (Form + Dynamic Graph)  
- **Description**: Interactive form to explore complaints by borough, date, hour, and temperature range, with arrow buttons to navigate.  
- **Sample Link**: [http://127.0.0.1:5000/tempComplaintVisualizer](http://127.0.0.1:5000/tempComplaintVisualizer)

---


##  Appendix: Code & APIs

- **API Source**: [https://apps.clarksonmsda.org/](https://apps.clarksonmsda.org/)
- **Weather API Code**: [GitHub - weather_api](https://github.com/whysoserious-joker/weather_api)
- **Libraries Used**:
  - `Flask` - backend
  - `PyMySQL` - DB integration
  - `Chart.js` - chart rendering
  - `matplotlib` - EDA plots
  - `PyYAML` - config loading

---

##  Developed For

**IA-626 Final Project**  
Clarkson University

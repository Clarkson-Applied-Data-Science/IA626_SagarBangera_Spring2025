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
- Performed Exploratory Data Analysis (EDA).
- Included: distribution by hour, temperature ranges, and complaints per borough.
- Visualized temporal and weather-based complaint patterns.

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

##  Sample Links

- Hourly breakdown: `/getHourlyComplaints?key=123`
- Hourly graph: `/graph`
- Date range input: `/dateRangeInput`
- Combined filtering: `/dateHourData?start=2015-12-01&end=2015-12-31&start_hr=18&end_hr=2&key=123`
- Night vs Day: `/nightDayPatterns?key=123`
- Top complaints by temperature: `/topComplaintTypesByTemp?key=123`
- Interactive Temp Pattern: `/tempPatternInput`

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

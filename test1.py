import requests
import csv
from datetime import datetime, timedelta
from time import sleep

API_KEY = "123"
BASE_URL = "https://apps.clarksonmsda.org/getData_by_zip_by_date_all_hours"

borough_zip_map = {
    "Manhattan": "10025",
    "Brooklyn": "11201",
    "Queens": "11373",
    "Bronx": "10453",
    "Staten Island": "10301"
}

start_date = datetime(2015, 7, 1)
end_date = datetime(2015, 12, 31)

output_file = "nyc_hourly_weather_2015_H2.csv"

with open(output_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["date", "hour", "borough", "zipcode", "temperature_C"])

    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        for borough, zip_code in borough_zip_map.items():
            url = f"{BASE_URL}?key={API_KEY}&zipcode={zip_code}&date={date_str}"
            try:
                res = requests.get(url)
                if res.status_code == 200:
                    data = res.json()
                    hour_data = data["results"][0]["hour"]
                    for hour_dict in hour_data:
                        for hour, info in hour_dict.items():
                            temp = info["weather"]["air_temperature"]["temperature"]
                            writer.writerow([date_str, hour, borough, zip_code, temp])
                    print(f" {borough} on {date_str}")
                else:
                    print(f" Failed for {borough} on {date_str}: {res.status_code}")
            except Exception as e:
                print(f" Error for {borough} on {date_str}: {e}")
            sleep(0.3)  

        current_date += timedelta(days=1)

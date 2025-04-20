import csv
from datetime import datetime

weather_file = "nyc_weather_cleaned.csv"
complaints_file = "311_Service_Requests_from_2010_to_Present.csv"
output_file = "merged_complaints_weather.csv"

weather_data = {}
with open(weather_file, "r") as wf:
    reader = csv.DictReader(wf)
    for row in reader:
        date = row["date"]
        hour = row["hour"]
        borough = row["borough"].strip().upper()
        key = (date, hour, borough)
        weather_data[key] = row["temperature_C"]

merged_count = 0
skipped_count = 0

with open(complaints_file, "r") as cf, open(output_file, "w", newline="") as outf:
    reader = csv.DictReader(cf)
    fieldnames = ["date", "hour", "borough", "temperature_C", "complaint_type", "descriptor", "location_type"]
    writer = csv.DictWriter(outf, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        try:
            raw_date = row["Created Date"]
            borough = row["Borough"].strip().upper()
            complaint = row["Complaint Type"]
            descriptor = row["Descriptor"]
            location = row["Location Type"]

            dt = datetime.strptime(raw_date, "%m/%d/%Y %I:%M:%S %p")
            date = dt.strftime("%Y-%m-%d")
            hour = str(dt.hour)

            key = (date, hour, borough)

            if key in weather_data:
                writer.writerow({
                    "date": date,
                    "hour": hour,
                    "borough": borough,
                    "temperature_C": weather_data[key],
                    "complaint_type": complaint,
                    "descriptor": descriptor,
                    "location_type": location
                })
                merged_count += 1
            else:
                skipped_count += 1

        except Exception:
            skipped_count += 1

print(f"Merged: {merged_count} rows")
print(f"Skipped: {skipped_count} rows (no temperature found or parse error)")

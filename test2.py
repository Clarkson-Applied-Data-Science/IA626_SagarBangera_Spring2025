import csv
from datetime import datetime

input_file = "nyc_hourly_weather_2015.csv"
output_file = "nyc_weather_cleaned.csv"
skipped_log = "skipped_temperatures_log.csv"

fixed = 0
skipped = 0
skipped_rows = []

with open(input_file, "r") as infile, open(output_file, "w", newline="") as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    for i, row in enumerate(reader):
        if row[0] == "date":
            writer.writerow(row)
        else:
            try:
                temp = float(row[4])
                row[4] = str(temp / 10)

                try:
                    original_date = row[0]
                    dt = datetime.strptime(original_date, "%d-%m-%Y")
                    row[0] = dt.strftime("%Y-%m-%d")
                except ValueError:
                    pass  

                fixed += 1
            except (ValueError, TypeError):
                row[4] = ""
                skipped_rows.append(row)
                skipped += 1
            writer.writerow(row)


with open(skipped_log, "w", newline="") as skipfile:
    writer = csv.writer(skipfile)
    writer.writerow(["date", "hour", "borough", "zipcode", "temperature"])
    writer.writerows(skipped_rows)

print("Done cleaning and reformatting!")
print(f"Temperatures fixed: {fixed}")
print(f"Temperatures skipped (invalid): {skipped}")
print(f"Skipped rows saved to: {skipped_log}")

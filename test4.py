# %%
import pymysql, csv, yaml

with open("config.yaml", 'r') as file:
    config = yaml.safe_load(file)

db_config = config['db']

conn = pymysql.connect(
    host=db_config['host'],
    port=db_config['port'],
    user=db_config['user'],
    passwd=db_config['passwd'],
    db=db_config['db'],
    autocommit=True
)
cur = conn.cursor()

with open("merged_complaints_weather.csv", encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = []
    for row in reader:
        rows.append((
            row['date'],
            int(row['hour']),
            row['borough'],
            float(row['temperature_C']) if row['temperature_C'] else None,
            row['complaint_type'],
            row['descriptor'],
            row['location_type']
        ))

insert_query = '''
INSERT INTO nyc_complaints (date, hour, borough, temperature_C, complaint_type, descriptor, location_type)
VALUES (%s, %s, %s, %s, %s, %s, %s);
'''

cur.executemany(insert_query, rows)
print(f"Inserted {len(rows)} rows.")




from flask import Flask, request, jsonify, render_template_string
import pymysql
import time
import json
import yaml


app = Flask(__name__)

def get_connection():
    with open("config.yaml", 'r') as file:
        config = yaml.safe_load(file)
    db_config = config['db']

    return pymysql.connect(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        passwd=db_config['passwd'],
        db=db_config['db'],
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def home():
    return '''
    <h2>Hourly Borough Complaint App</h2>
    <ul>
        <li><a href="/getHourlyComplaints?key=123">Get JSON</a></li>
        <li><a href="/graph">View Graph</a></li>
    </ul>
    '''

@app.route('/getHourlyComplaints')
def get_hourly_complaints():
    key = request.args.get('key')
    res = {'req': 'getHourlyComplaints'}

    if key != '123':
        res['code'] = 0
        res['msg'] = 'Invalid key'
        return jsonify(res)

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        sql = """
            SELECT hour AS hr, borough, COUNT(*) AS cnt
            FROM nyc_complaints
            WHERE borough IN ('MANHATTAN', 'BROOKLYN', 'QUEENS', 'BRONX', 'STATEN ISLAND')
            GROUP BY hr, borough
            ORDER BY hr, borough
        """
        t0 = time.time()
        cur.execute(sql)
        rows = cur.fetchall()
        t1 = time.time()

        res.update({
            'code': 1,
            'msg': 'ok',
            'sqltime': round(t1 - t0, 4),
            'data': rows
        })

    except Exception as e:
        res.update({'code': 0, 'msg': f'Error: {str(e)}'})

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return jsonify(res)

@app.route('/graph')
def graph():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT hour AS hr, borough, COUNT(*) AS cnt
        FROM nyc_complaints
        WHERE borough IN ('MANHATTAN', 'BROOKLYN', 'QUEENS', 'BRONX', 'STATEN ISLAND')
        GROUP BY hr, borough
        ORDER BY hr, borough
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()

    data_by_borough = {}
    for row in data:
        b = row['borough']
        if b not in data_by_borough:
            data_by_borough[b] = [0]*24
        data_by_borough[b][row['hr']] = row['cnt']

    hours = list(range(24))

    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hourly Complaints by Borough</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <h3>Hourly Complaint Count by Borough</h3>
        <canvas id="barChart" width="1000" height="500"></canvas>
        <script>
            const ctx = document.getElementById('barChart').getContext('2d');
            const chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: {{ hours | safe }},
                    datasets: [
                        {% for borough, counts in data.items() %}
                        {
                            label: '{{ borough }}',
                            data: {{ counts | safe }},
                        },
                        {% endfor %}
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: { title: { display: true, text: 'Hour of Day' }},
                        y: { title: { display: true, text: 'Number of Complaints' }}
                    }
                }
            });
        </script>
    </body>
    </html>
    ''', hours=hours, data=data_by_borough)

@app.route('/hourlyInput')
def hourly_input():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Select Hour</title>
    </head>
    <body>
        <h3>View Borough Complaints for a Specific Hour</h3>
        <form action="/hourlyData" method="get">
            <label for="hour">Select Hour (0-23):</label>
            <input type="number" name="hour" min="0" max="23" required>
            <button type="submit">Submit</button>
        </form>
    </body>
    </html>
    '''

@app.route('/hourlyData')
def hourly_data():
    try:
        hour = int(request.args.get('hour'))
        if not (0 <= hour <= 23):
            return "Hour must be between 0 and 23"

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT borough, COUNT(*) AS cnt
            FROM nyc_complaints
            WHERE hour = %s AND borough IN ('MANHATTAN', 'BROOKLYN', 'QUEENS', 'BRONX', 'STATEN ISLAND')
            GROUP BY borough
            ORDER BY borough
        """, (hour,))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        boroughs = [row['borough'] for row in rows]
        counts = [row['cnt'] for row in rows]

        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Hourly Breakdown</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body>
            <h3>Complaint Counts at Hour {{ hour }}</h3>
            <canvas id="hourChart" width="800" height="400"></canvas>
            <script>
                const ctx = document.getElementById('hourChart').getContext('2d');
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: {{ boroughs | safe }},
                        datasets: [{
                            label: 'Complaints',
                            data: {{ counts | safe }},
                            backgroundColor: 'rgba(54, 162, 235, 0.6)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: {
                            y: { beginAtZero: true }
                        }
                    }
                });
            </script>
        </body>
        </html>
        ''', hour=hour, boroughs=boroughs, counts=counts)

    except Exception as e:
        return f" Error: {e}"
    

@app.route('/dateRangeInput')
def date_range_input():
    return '''
    <h2>Select Date Range</h2>
    <form action="/dateRangeData" method="get">
    Start Date (YYYY-MM-DD): <input type="text" name="start"><br>
    End Date (YYYY-MM-DD): <input type="text" name="end"><br>
    <input type="hidden" name="key" value="123">
    <input type="submit" value="Submit">
    </form>
    '''


@app.route('/dateRangeData')
def date_range_data():
    start = request.args.get('start')
    end = request.args.get('end')
    key = request.args.get('key')

    res = {'req': 'dateRangeData'}

    if key != '123':
        res['code'] = 0
        res['msg'] = 'Invalid key'
        return jsonify(res)

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        sql = """
            SELECT borough, COUNT(*) AS cnt
            FROM nyc_complaints
            WHERE borough IN ('MANHATTAN', 'BROOKLYN', 'QUEENS', 'BRONX', 'STATEN ISLAND')
              AND date BETWEEN %s AND %s
            GROUP BY borough
            ORDER BY borough
        """
        t0 = time.time()
        cur.execute(sql, (start, end))
        rows = cur.fetchall()
        t1 = time.time()

        boroughs = [row['borough'] for row in rows]
        counts = [row['cnt'] for row in rows]

        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Borough Complaints by Date Range</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body>
            <h3>Borough Complaint Count from {{ start }} to {{ end }}</h3>
            <canvas id="barChart" width="800" height="400"></canvas>
            <script>
                const ctx = document.getElementById('barChart').getContext('2d');
                const chart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: {{ boroughs | safe }},
                        datasets: [{
                            label: 'Complaint Count',
                            data: {{ counts | safe }}
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: { beginAtZero: true, title: { display: true, text: 'Number of Complaints' }},
                            x: { title: { display: true, text: 'Borough' }}
                        }
                    }
                });
            </script>
        </body>
        </html>
        ''', start=start, end=end, boroughs=boroughs, counts=counts)

    except Exception as e:
        res['code'] = 0
        res['msg'] = f'Error: {str(e)}'
        return jsonify(res)

    finally:
        try:
            if cur: cur.close()
        except: pass
        try:
            if conn: conn.close()
        except: pass

@app.route('/dateHourInput')
def date_hour_input():
    return '''
    <h2>Select Date & Hour Range</h2>
    <form action="/dateHourData" method="get">
        Start Date (YYYY-MM-DD): <input type="text" name="start"><br>
        End Date (YYYY-MM-DD): <input type="text" name="end"><br>
        Start Hour (0-23): <input type="number" name="start_hr" min="0" max="23"><br>
        End Hour (0-23): <input type="number" name="end_hr" min="0" max="23"><br>
        <input type="hidden" name="key" value="123">
        <input type="submit" value="Submit">
    </form>
    '''

@app.route('/dateHourData')
def date_hour_data():
    start = request.args.get('start')
    end = request.args.get('end')
    start_hr = request.args.get('start_hr', type=int)
    end_hr = request.args.get('end_hr', type=int)
    key = request.args.get('key')

    res = {'req': 'dateHourData'}

    if key != '123':
        res['code'] = 0
        res['msg'] = 'Invalid key'
        return jsonify(res)

    try:
        conn = get_connection()
        cur = conn.cursor()

        if start_hr <= end_hr:
            hour_condition = "hour BETWEEN %s AND %s"
            hour_params = (start_hr, end_hr)
            hours = list(range(start_hr, end_hr + 1))
        else:
            hour_condition = "(hour >= %s OR hour <= %s)"
            hour_params = (start_hr, end_hr)
            hours = list(range(start_hr, 24)) + list(range(0, end_hr + 1))

        sql = f"""
            SELECT hour AS hr, borough, COUNT(*) AS cnt
            FROM nyc_complaints
            WHERE borough IN ('MANHATTAN', 'BROOKLYN', 'QUEENS', 'BRONX', 'STATEN ISLAND')
              AND date BETWEEN %s AND %s
              AND {hour_condition}
            GROUP BY hr, borough
            ORDER BY hr, borough
        """

        t0 = time.time()
        cur.execute(sql, (start, end, *hour_params))
        rows = cur.fetchall()
        t1 = time.time()

        cur.close()
        conn.close()

        data_by_borough = {}
        for row in rows:
            b = row['borough']
            h = row['hr']
            if b not in data_by_borough:
                data_by_borough[b] = {}
            data_by_borough[b][h] = row['cnt']

        final_data = {}
        for b in data_by_borough:
            final_data[b] = [data_by_borough[b].get(h, 0) for h in hours]

        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Borough Complaints (Date & Hour Range)</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body>
            <h3>Complaints from {{ start }} to {{ end }} (Hours {{ start_hr }}–{{ end_hr }})</h3>
            <canvas id="barChart" width="1000" height="500"></canvas>
            <script>
                const ctx = document.getElementById('barChart').getContext('2d');
                const chart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: {{ hours | safe }},
                        datasets: [
                            {% for borough, counts in data.items() %}
                            {
                                label: '{{ borough }}',
                                data: {{ counts | safe }},
                            },
                            {% endfor %}
                        ]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            x: { title: { display: true, text: 'Hour of Day' }},
                            y: { title: { display: true, text: 'Number of Complaints' }}
                        }
                    }
                });
            </script>
        </body>
        </html>
        ''', start=start, end=end, start_hr=start_hr, end_hr=end_hr, hours=hours, data=final_data)

    except Exception as e:
        res['code'] = 0
        res['msg'] = f'Error: {str(e)}'
        return jsonify(res)


TIME_BUCKETS = {
    'night': (0, 5),
    'morning': (6, 11),
    'afternoon': (12, 17),
    'evening': (18, 23)
}

@app.route('/topComplaintsByTime')
def top_complaints_by_time():
    key = request.args.get('key')
    bucket = request.args.get('bucket', 'night').lower()

    res = {'req': 'topComplaintsByTime'}

    if key != '123':
        res['code'] = 0
        res['msg'] = 'Invalid key'
        return jsonify(res)

    if bucket not in TIME_BUCKETS:
        res['code'] = 0
        res['msg'] = f"Invalid time bucket. Choose from {list(TIME_BUCKETS.keys())}"
        return jsonify(res)

    start_hr, end_hr = TIME_BUCKETS[bucket]
    conn = get_connection()
    cur = conn.cursor()

    sql = '''
        SELECT borough, complaint_type, COUNT(*) as cnt
        FROM nyc_complaints
        WHERE hour BETWEEN %s AND %s
        AND borough IN ('MANHATTAN','BROOKLYN','QUEENS','BRONX','STATEN ISLAND')
        GROUP BY borough, complaint_type
        ORDER BY borough, cnt DESC
    '''

    t0 = time.time()
    cur.execute(sql, (start_hr, end_hr))
    rows = cur.fetchall()
    t1 = time.time()

    cur.close()
    conn.close()

    top_complaints = []
    borough_counts = {}
    for row in rows:
        b = row['borough']
        if b not in borough_counts:
            borough_counts[b] = 0
        if borough_counts[b] < 3:
            top_complaints.append(row)
            borough_counts[b] += 1


    labels = list(set([row['complaint_type'] for row in top_complaints]))
    labels.sort()
    boroughs = ['MANHATTAN', 'BROOKLYN', 'QUEENS', 'BRONX', 'STATEN ISLAND']
    dataset = {b: [0]*len(labels) for b in boroughs}
    for row in top_complaints:
        b = row['borough']
        idx = labels.index(row['complaint_type'])
        dataset[b][idx] = row['cnt']

    res.update({
        'code': 1,
        'msg': 'ok',
        'sqltime': round(t1 - t0, 4),
        'data': top_complaints
    })

    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Top Complaints by Time</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <h3>Top Complaint Types During {{ bucket.title() }} ({{ start_hr }}:00 - {{ end_hr }}:59)</h3>
        <canvas id="barChart" width="1000" height="500"></canvas>
        <script>
            const ctx = document.getElementById('barChart').getContext('2d');
            const chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: {{ labels | safe }},
                    datasets: [
                        {% for borough, values in dataset.items() %}
                        {
                            label: '{{ borough }}',
                            data: {{ values | safe }}
                        },
                        {% endfor %}
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: { title: { display: true, text: 'Complaint Type' }},
                        y: { title: { display: true, text: 'Complaint Count' }, beginAtZero: true }
                    }
                }
            });
        </script>
    </body>
    </html>
    ''', bucket=bucket, start_hr=start_hr, end_hr=end_hr, labels=labels, dataset=dataset)

@app.route('/complaintsByTempBucket')
def complaints_by_temp():
    key = request.args.get('key')
    res = {'req': 'complaintsByTempBucket'}

    if key != '123':
        res['code'] = 0
        res['msg'] = 'Invalid key'
        return jsonify(res)

    try:
        conn = get_connection()
        cur = conn.cursor()

        sql = """
            SELECT 
                CASE 
                    WHEN temperature_C < 0 THEN '< 0°C'
                    WHEN temperature_C BETWEEN 0 AND 10 THEN '0-10°C'
                    WHEN temperature_C BETWEEN 10 AND 20 THEN '10-20°C'
                    ELSE '> 20°C'
                END AS temp_bucket,
                COUNT(*) AS count
            FROM nyc_complaints
            WHERE temperature_C IS NOT NULL
            GROUP BY temp_bucket
            ORDER BY count DESC
        """

        t0 = time.time()
        cur.execute(sql)
        rows = cur.fetchall()
        t1 = time.time()

        res.update({
            'code': 1,
            'msg': 'ok',
            'sqltime': round(t1 - t0, 4),
            'data': rows
        })

    except Exception as e:
        res.update({'code': 0, 'msg': f'Error: {str(e)}'})

    finally:
        if conn: conn.close()

    return jsonify(res)

@app.route('/topComplaintTypesByTemp')
def top_complaints_by_temp():
    key = request.args.get('key')
    res = {'req': 'topComplaintTypesByTemp'}

    if key != '123':
        res['code'] = 0
        res['msg'] = 'Invalid key'
        return jsonify(res)

    temp_ranges = [
        ('< 0°C', "temperature_C < 0"),
        ('0-10°C', "temperature_C >= 0 AND temperature_C < 10"),
        ('10-20°C', "temperature_C >= 10 AND temperature_C <= 20"),
        ('> 20°C', "temperature_C > 20")
    ]

    all_results = []
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        t0 = time.time()

        for label, condition in temp_ranges:
            cur.execute(f'''
                SELECT complaint_type, COUNT(*) as cnt
                FROM nyc_complaints
                WHERE {condition}
                GROUP BY complaint_type
                ORDER BY cnt DESC
                LIMIT 20
            ''')
            data = cur.fetchall()
            for row in data:
                row['temp_bucket'] = label
                all_results.append(row)

        t1 = time.time()
        res.update({
            'code': 1,
            'msg': 'ok',
            'sqltime': round(t1 - t0, 4),
            'data': all_results
        })

    except Exception as e:
        res['code'] = 0
        res['msg'] = f'Error: {str(e)}'

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return jsonify(res)


@app.route('/boroughComplaintsByTemp')
def borough_temp():
    key = request.args.get('key')
    res = {'req': 'boroughComplaintsByTemp'}

    if key != '123':
        res['code'] = 0
        res['msg'] = 'Invalid key'
        return jsonify(res)

    try:
        conn = get_connection()
        cur = conn.cursor()

        sql = """
            SELECT 
                borough,
                CASE 
                    WHEN temperature_C < 0 THEN '< 0°C'
                    WHEN temperature_C BETWEEN 0 AND 10 THEN '0-10°C'
                    WHEN temperature_C BETWEEN 10 AND 20 THEN '10-20°C'
                    ELSE '> 20°C'
                END AS temp_bucket,
                COUNT(*) AS count
            FROM nyc_complaints
            WHERE temperature_C IS NOT NULL
              AND borough IN ('MANHATTAN', 'BROOKLYN', 'QUEENS', 'BRONX', 'STATEN ISLAND')
            GROUP BY temp_bucket, borough
            ORDER BY temp_bucket, count DESC
        """

        t0 = time.time()
        cur.execute(sql)
        rows = cur.fetchall()
        t1 = time.time()

        res.update({
            'code': 1,
            'msg': 'ok',
            'sqltime': round(t1 - t0, 4),
            'data': rows
        })

    except Exception as e:
        res.update({'code': 0, 'msg': f'Error: {str(e)}'})

    finally:
        if conn: conn.close()

    return jsonify(res)

@app.route('/tempComplaintVisualizer')
def temp_complaint_visualizer():
    return '''
    <h2>Select Date & Hour Range and Borough</h2>
    <form action="/complaintsByTempRange" method="get">
        Start Date (YYYY-MM-DD): <input type="text" name="start"><br>
        End Date (YYYY-MM-DD): <input type="text" name="end"><br>
        Start Hour (0–23): <input type="number" name="start_hr" min="0" max="23"><br>
        End Hour (0–23): <input type="number" name="end_hr" min="0" max="23"><br>
        Borough: <select name="borough">
            <option value="MANHATTAN">MANHATTAN</option>
            <option value="BROOKLYN">BROOKLYN</option>
            <option value="QUEENS">QUEENS</option>
            <option value="BRONX">BRONX</option>
            <option value="STATEN ISLAND">STATEN ISLAND</option>
        </select><br>
        <input type="hidden" name="key" value="123">
        <input type="submit" value="Submit">
    </form>
    '''

@app.route('/complaintsByTempRange')
def complaints_by_temp_range():
    start = request.args.get('start')
    end = request.args.get('end')
    start_hr = int(request.args.get('start_hr'))
    end_hr = int(request.args.get('end_hr'))
    borough = request.args.get('borough')
    key = request.args.get('key')

    res = {'req': 'complaintsByTempRange'}

    if key != '123':
        res['code'] = 0
        res['msg'] = 'Invalid key'
        return jsonify(res)

    try:
        conn = get_connection()
        cur = conn.cursor()

        if start_hr <= end_hr:
            hour_clause = "hour BETWEEN %s AND %s"
            hour_params = (start_hr, end_hr)
        else:
            hour_clause = "(hour >= %s OR hour <= %s)"
            hour_params = (start_hr, end_hr)

        sql = f'''
            SELECT
                CASE
                    WHEN temperature_C < 0 THEN '< 0°C'
                    WHEN temperature_C BETWEEN 0 AND 10 THEN '0-10°C'
                    WHEN temperature_C BETWEEN 10 AND 20 THEN '10-20°C'
                    ELSE '> 20°C'
                END AS temp_bucket,
                complaint_type,
                COUNT(*) as cnt
            FROM nyc_complaints
            WHERE borough = %s
              AND date BETWEEN %s AND %s
              AND {hour_clause}
            GROUP BY temp_bucket, complaint_type
            ORDER BY temp_bucket, cnt DESC
        '''

        t0 = time.time()
        cur.execute(sql, (borough, start, end, *hour_params))
        rows = cur.fetchall()
        t1 = time.time()

        cur.close()
        conn.close()

        # Organize data for chart
        buckets = {}
        for row in rows:
            bucket = row['temp_bucket']
            if bucket not in buckets:
                buckets[bucket] = []
            buckets[bucket].append({
                'complaint_type': row['complaint_type'],
                'cnt': row['cnt']
            })

        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Complaints by Temperature Bucket</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        </head>
        <body>
            <h3>Complaint Types by Temperature ({{ borough }})<br>From {{ start }} to {{ end }}, Hours {{ start_hr }}–{{ end_hr }}</h3>
            {% for bucket, values in buckets.items() %}
                <h4>{{ bucket }}</h4>
                <canvas id="chart_{{ loop.index }}" width="900" height="400"></canvas>
                <script>
                    new Chart(document.getElementById("chart_{{ loop.index }}").getContext('2d'), {
                        type: 'bar',
                        data: {
                            labels: {{ values|map(attribute='complaint_type')|list|safe }},
                            datasets: [{
                                label: 'Complaint Count',
                                data: {{ values|map(attribute='cnt')|list|safe }}
                            }]
                        },
                        options: {
                            responsive: true,
                            scales: {
                                y: { beginAtZero: true, title: { display: true, text: 'Count' }},
                                x: { title: { display: true, text: 'Complaint Type' }, ticks: { maxRotation: 90, minRotation: 60 } }
                            }
                        }
                    });
                </script>
            {% endfor %}
        </body>
        </html>
        ''', buckets=buckets, borough=borough, start=start, end=end, start_hr=start_hr, end_hr=end_hr)

    except Exception as e:
        res['code'] = 0
        res['msg'] = f'Error: {str(e)}'
        return jsonify(res)
    
if __name__ == '__main__':
    app.run(debug=True)

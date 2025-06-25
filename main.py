import os
import pandas as pd
from flask import Flask, render_template
from matplotlib import pyplot as plt
import time
from datetime import datetime
import logging

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = 'super-secret-key'

logging.basicConfig(
    filename='app.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s' 
)
LOG_FILE_PATH = r'C:\Users\pavlo\Downloads\Free6\all_logs\server_errors.log'

import re

def parse_log_file():
    timestamps = []
    event_types = []
    messages = []

    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

    try:
        with open(LOG_FILE_PATH, 'r', encoding='utf-8') as file:
            for line in file:
                try:
                    line = ansi_escape.sub('', line)

                    match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)', line)
                    if not match:
                        continue
                    
                    timestamp_str = match.group(1)
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')

                    http_match = re.search(r'"([A-Z]+) (.*?) HTTP.*?" (\d{3})', line)
                    if http_match:
                        method = http_match.group(1)
                        path = http_match.group(2)
                        status = int(http_match.group(3))
                        msg = f'{method} {path} -> {status}'

                        if status == 404:
                            event_type = 'Not Found'
                        elif status >= 500:
                            event_type = 'Server Error'
                        elif status == 200:
                            event_type = 'OK'
                        elif status == 206:
                            event_type = 'Partial Content'
                        else:
                            event_type = f'Status {status}'
                    else:
                        msg = line.strip()
                        event_type = 'Other'

                    timestamps.append(timestamp)
                    event_types.append(event_type)
                    messages.append(msg)

                except Exception as e:
                    continue
    except FileNotFoundError:
        print(f"Файл не найден: {LOG_FILE_PATH}")
        return pd.DataFrame({'timestamp': [], 'event_type': [], 'message': []})
    
    return pd.DataFrame({'timestamp': timestamps, 'event_type': event_types, 'message': messages})


@app.route('/')
def index():
    df = parse_log_file()

    if df.empty:
        return render_template('index.html', image=None, table_data=None, error="Нет данных в лог-файле или файл не найден")

    event_counts = df['event_type'].value_counts()

    plt.figure(figsize=(8, 6))
    event_counts.plot(kind='bar', color='crimson')
    plt.title('Распределение событий по типам')
    plt.xlabel('Тип события')
    plt.ylabel('Количество')
    plt.grid(axis='y')
    plt.xticks(rotation=45)


    image_path = 'static/event_type_chart.png'
    plt.tight_layout()
    plt.savefig(image_path)
    plt.close()

    table_data = df[['timestamp', 'event_type', 'message']].to_dict('records')

    image_url = f'{image_path}?t={int(time.time())}'

    return render_template('index.html', image=image_url, table_data=table_data)

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(host='0.0.0.0', port=8099, debug=False)
import csv
import time
import requests
import os

SERVER_URL = os.environ.get('SERVER_URL', 'http://localhost:5000')
SPEED_FACTOR = float(os.environ.get('SPEED_FACTOR', '10'))
CSV_FILE = os.environ.get('CSV_FILE', '/data/ip_addresses.csv')


def read_csv(filepath):
    packages = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            packages.append({
                'ip': row['ip address'],
                'lat': float(row['Latitude']),
                'lon': float(row['Longitude']),
                'timestamp': float(row['Timestamp']),
                'suspicious': int(float(row['suspicious']))
            })
    return sorted(packages, key=lambda x: x['timestamp'])


def wait_for_server():
    print(f"Waiting for server at {SERVER_URL}...")
    while True:
        try:
            r = requests.get(f'{SERVER_URL}/health', timeout=2)
            if r.status_code == 200:
                print("Server is ready!")
                return
        except Exception:
            pass
        time.sleep(1)


def send_packages(packages):
    start_ts = packages[0]['timestamp']
    real_start = time.time()

    for i, pkg in enumerate(packages):
        expected_delay = (pkg['timestamp'] - start_ts) / SPEED_FACTOR
        elapsed = time.time() - real_start
        sleep_time = expected_delay - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

        try:
            requests.get(
                f'{SERVER_URL}/receive',
                params={
                    'ip': pkg['ip'],
                    'lat': pkg['lat'],
                    'lon': pkg['lon'],
                    'timestamp': pkg['timestamp'],
                    'suspicious': pkg['suspicious']
                },
                timeout=5
            )
        except Exception as e:
            print(f"Error sending package {i}: {e}")

        if (i + 1) % 200 == 0:
            print(f"Sent {i + 1}/{len(packages)} packages...")

    print("Done sending all packages!")


if __name__ == '__main__':
    print(f"Reading CSV from {CSV_FILE}")
    packages = read_csv(CSV_FILE)
    span = packages[-1]['timestamp'] - packages[0]['timestamp']
    print(f"Loaded {len(packages)} packages spanning {span:.0f} seconds")
    print(f"Speed factor: {SPEED_FACTOR}x  (playback ~{span/SPEED_FACTOR:.0f}s)")

    wait_for_server()
    time.sleep(2)

    print("Sending packages...")
    send_packages(packages)

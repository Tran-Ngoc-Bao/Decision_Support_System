#!/usr/bin/env python3
"""
Geocode addresses using Nominatim (OpenStreetMap) and write results to CSV.

Usage:
  pip install -r requirements.txt
  python geocode_nominatim.py --input addresses.txt --output results.csv
  OR
  python geocode_nominatim.py --input addresses.csv --column address --output results.csv
"""
import argparse
import csv
import json
import sys
from time import sleep

try:
    from geopy.geocoders import Nominatim
    from geopy.extra.rate_limiter import RateLimiter
except ImportError:
    print("Please install geopy: pip install geopy")
    sys.exit(1)

def read_input_lines(input_path, column=None):
    if input_path.lower().endswith('.csv') and column:
        rows = []
        with open(input_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if column not in reader.fieldnames:
                raise ValueError(f"Column '{column}' not found in CSV")
            for r in reader:
                rows.append(r[column])
        return rows
    else:
        with open(input_path, encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]

def main():
    p = argparse.ArgumentParser(description="Geocode addresses via Nominatim")
    p.add_argument('--input', '-i', required=True, help='Input file: .txt (one address per line) or .csv')
    p.add_argument('--column', '-c', help='If input is CSV, name of column that contains addresses')
    p.add_argument('--output', '-o', default='geocoded.csv', help='Output CSV path')
    p.add_argument('--email', help='Contact email to set as User-Agent (recommended)')
    p.add_argument('--delay', type=float, default=1.0, help='Seconds between requests (respect Nominatim usage policy)')
    args = p.parse_args()

    addresses = read_input_lines(args.input, column=args.column)
    geolocator = Nominatim(user_agent=args.email or "geocode-script")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=args.delay, max_retries=2, error_wait_seconds=5.0)

    with open(args.output, 'w', newline='', encoding='utf-8') as outf:
        fieldnames = ['input_address', 'status', 'latitude', 'longitude', 'display_name', 'raw_json']
        writer = csv.DictWriter(outf, fieldnames=fieldnames)
        writer.writeheader()

        for addr in addresses:
            try:
                location = geocode(addr, addressdetails=False, timeout=10)
                if location:
                    writer.writerow({
                        'input_address': addr,
                        'status': 'ok',
                        'latitude': location.latitude,
                        'longitude': location.longitude,
                        'display_name': location.address,
                        'raw_json': json.dumps(location.raw, ensure_ascii=False)
                    })
                else:
                    writer.writerow({
                        'input_address': addr,
                        'status': 'not_found',
                        'latitude': '',
                        'longitude': '',
                        'display_name': '',
                        'raw_json': ''
                    })
            except Exception as e:
                writer.writerow({
                    'input_address': addr,
                    'status': f'error: {str(e)}',
                    'latitude': '',
                    'longitude': '',
                    'display_name': '',
                    'raw_json': ''
                })
            # Respectful pause is handled by RateLimiter but extra safety:
            sleep(0.1)

    print(f"Done. Results saved to {args.output}")

if __name__ == "__main__":
    main()
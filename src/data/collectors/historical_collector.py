"""
historical_data_collector.py
Automatically download and consolidate historical AQI data
"""

import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import os


class HistoricalDataCollector:
    """
    Collect historical air quality data from multiple sources
    """

    def __init__(self, start_date, end_date, cities=None):
        """
        Parameters:
        -----------
        start_date : str, format 'YYYY-MM-DD'
        end_date : str, format 'YYYY-MM-DD'
        cities : list, optional list of cities
        """
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.cities = cities or ['Delhi', 'Mumbai', 'Bangalore', 'Kolkata', 'Chennai']

        # API endpoints (example - adjust to actual data.gov.in API)
        self.base_url = "https://api.data.gov.in/resource/"
        self.api_key = "YOUR_API_KEY"  # Get from data.gov.in

    def download_cpcb_data(self, date):
        """Download data for a specific date from CPCB"""
        endpoint = f"{self.base_url}/air-quality"

        params = {
            'api-key': self.api_key,
            'format': 'json',
            'date': date.strftime('%Y-%m-%d'),
            'limit': 10000
        }

        try:
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return pd.DataFrame(data.get('records', []))
        except Exception as e:
            print(f"Error downloading data for {date}: {e}")
            return pd.DataFrame()

    def collect_range(self, save_path='data/historical'):
        """
        Collect data for entire date range
        """
        os.makedirs(save_path, exist_ok=True)

        all_data = []
        current_date = self.start_date

        print(f"Collecting data from {self.start_date} to {self.end_date}")

        while current_date <= self.end_date:
            print(f"Downloading: {current_date.strftime('%Y-%m-%d')}", end='\r')

            df = self.download_cpcb_data(current_date)

            if not df.empty:
                df['collection_date'] = current_date
                all_data.append(df)

                # Save daily file
                filename = f"{save_path}/aqi_{current_date.strftime('%Y%m%d')}.csv"
                df.to_csv(filename, index=False)

            current_date += timedelta(days=1)
            time.sleep(1)  # Rate limiting

        # Combine all data
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            combined_df.to_csv(f"{save_path}/combined_historical.csv", index=False)
            print(f"\n✓ Collected {len(combined_df)} records")
            return combined_df
        else:
            print("\n✗ No data collected")
            return pd.DataFrame()


def consolidate_manual_downloads(folder_path='data/downloads'):
    """
    Consolidate manually downloaded CSV files
    """
    import glob

    csv_files = glob.glob(f"{folder_path}/*.csv")

    print(f"Found {len(csv_files)} CSV files")

    dfs = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            print(f"Loaded {file}: {len(df)} rows")
            dfs.append(df)
        except Exception as e:
            print(f"Error loading {file}: {e}")

    if dfs:
        combined = pd.concat(dfs, ignore_index=True)
        combined.to_csv('data/historical_combined.csv', index=False)
        print(f"\n✓ Combined data: {len(combined)} total rows")
        return combined

    return pd.DataFrame()


def validate_historical_data(df):
    """
    Validate and clean historical data
    """
    print("\n" + "=" * 60)
    print("Data Validation Report")
    print("=" * 60)

    # 1. Check date coverage
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        print(f"Date Range: {df['date'].min()} to {df['date'].max()}")
        print(f"Total Days: {(df['date'].max() - df['date'].min()).days}")

    # 2. Check missing values
    missing = df.isnull().sum()
    print(f"\nMissing Values:")
    print(missing[missing > 0] if missing.any() else "None")

    # 3. Check for duplicates
    if all(col in df.columns for col in ['date', 'city', 'station']):
        duplicates = df.duplicated(subset=['date', 'city', 'station']).sum()
        print(f"\nDuplicate Records: {duplicates}")

    # 4. Check value ranges
    print(f"\nValue Ranges:")
    for col in ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'OZONE']:
        if col in df.columns:
            print(f"{col}: {df[col].min():.1f} - {df[col].max():.1f}")

    print("=" * 60)

    return df


if __name__ == "__main__":
    # Usage example
    collector = HistoricalDataCollector(
        start_date='2026-03-01',
        end_date='2026-03-31'
    )

    # Note: This requires a valid API key from data.gov.in
    # historical_data = collector.collect_range()

    # For demo, create sample historical data
    print("Historical Data Collector Module Loaded")
    print("To collect data, provide a valid data.gov.in API key")
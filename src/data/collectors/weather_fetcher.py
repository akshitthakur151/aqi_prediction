"""
weather_data_fetcher.py
Fetch historical weather data for cities using Open-Meteo API
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time


class WeatherDataFetcher:
    """
    Fetch weather data from Open-Meteo (free, no API key required)
    """

    def __init__(self):
        self.base_url = "https://archive-api.open-meteo.com/v1/archive"

    def fetch_historical_weather(self, latitude, longitude,
                                  start_date, end_date):
        """
        Fetch historical weather data for a location.

        Parameters:
        -----------
        latitude, longitude : float
        start_date, end_date : str, format 'YYYY-MM-DD'

        Returns:
        --------
        DataFrame with weather data
        """
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'start_date': start_date,
            'end_date': end_date,
            'daily': [
                'temperature_2m_max',
                'temperature_2m_min',
                'temperature_2m_mean',
                'precipitation_sum',
                'windspeed_10m_max',
                'winddirection_10m_dominant'
            ],
            'hourly': [
                'temperature_2m',
                'relativehumidity_2m',
                'windspeed_10m',
                'pressure_msl'
            ],
            'timezone': 'Asia/Kolkata'
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Convert hourly data to DataFrame
            hourly_df = pd.DataFrame({
                'datetime': pd.to_datetime(data['hourly']['time']),
                'temperature': data['hourly']['temperature_2m'],
                'humidity': data['hourly']['relativehumidity_2m'],
                'wind_speed': data['hourly']['windspeed_10m'],
                'pressure': data['hourly']['pressure_msl']
            })

            # Add daily aggregates
            if 'daily' in data:
                daily_df = pd.DataFrame({
                    'date': pd.to_datetime(data['daily']['time']),
                    'temp_max': data['daily']['temperature_2m_max'],
                    'temp_min': data['daily']['temperature_2m_min'],
                    'temp_mean': data['daily']['temperature_2m_mean'],
                    'precipitation': data['daily']['precipitation_sum'],
                    'wind_max': data['daily']['windspeed_10m_max'],
                    'wind_dir': data['daily']['winddirection_10m_dominant']
                })

            return hourly_df

        except Exception as e:
            print(f"Error fetching weather: {e}")
            return pd.DataFrame()

    def fetch_for_cities(self, cities_dict, start_date, end_date):
        """
        Fetch weather for multiple cities.

        Parameters:
        -----------
        cities_dict : dict, {'city_name': (lat, lon)}
        """
        all_weather = []

        for city, (lat, lon) in cities_dict.items():
            print(f"Fetching weather for {city}...", end='\r')

            df = self.fetch_historical_weather(lat, lon, start_date, end_date)

            if not df.empty:
                df['city'] = city
                df['latitude'] = lat
                df['longitude'] = lon
                all_weather.append(df)

            time.sleep(0.5)  # Rate limiting

        if all_weather:
            combined = pd.concat(all_weather, ignore_index=True)
            print(f"\n✓ Weather data collected: {len(combined)} records")
            return combined

        print("\n✗ No weather data collected")
        return pd.DataFrame()


def merge_weather_aqi(aqi_df, weather_df):
    """
    Merge weather data with AQI data.

    Parameters:
    -----------
    aqi_df : DataFrame with AQI data and datetime column
    weather_df : DataFrame with weather data

    Returns:
    --------
    Merged DataFrame
    """
    # Ensure datetime columns
    aqi_df = aqi_df.copy()
    weather_df = weather_df.copy()

    aqi_df['datetime'] = pd.to_datetime(aqi_df['datetime'])
    weather_df['datetime'] = pd.to_datetime(weather_df['datetime'])

    # Round to nearest hour for matching
    aqi_df['datetime_hour'] = aqi_df['datetime'].dt.floor('H')
    weather_df['datetime_hour'] = weather_df['datetime'].dt.floor('H')

    # Merge on city and datetime
    merged = aqi_df.merge(
        weather_df,
        on=['city', 'datetime_hour'],
        how='left',
        suffixes=('', '_weather')
    )

    print(f"Merged data shape: {merged.shape}")
    print(f"Missing weather data: {merged['temperature'].isna().sum()} rows")

    return merged


# Example usage
if __name__ == "__main__":
    cities = {
        'Delhi': (28.6139, 77.2090),
        'Mumbai': (19.0760, 72.8777),
        'Bangalore': (12.9716, 77.5946),
        'Kolkata': (22.5726, 88.3639),
        'Chennai': (13.0827, 80.2707)
    }

    fetcher = WeatherDataFetcher()
    weather_data = fetcher.fetch_for_cities(
        cities,
        start_date='2026-03-01',
        end_date='2026-03-31'
    )

    if not weather_data.empty:
        weather_data.to_csv('../data/weather_historical.csv', index=False)
        print(f"✓ Weather data saved: {len(weather_data)} records")
# AQI Prediction - Advanced Implementation Guide
## From Basic Model to Production-Ready System

This guide covers all advanced features, deployment, and production-readiness.

---

## Table of Contents

### Part 1: Data Enhancement
1. [Historical Data Collection](#1-historical-data-collection)
2. [Weather Data Integration](#2-weather-data-integration)
3. [Traffic Data Integration](#3-traffic-data-integration)
4. [Additional External Features](#4-additional-external-features)

### Part 2: Advanced Modeling
5. [Time-Series Models (LSTM/GRU)](#5-time-series-models)
6. [Ensemble Methods](#6-ensemble-methods)
7. [Uncertainty Quantification](#7-uncertainty-quantification)
8. [Spatial Autocorrelation](#8-spatial-autocorrelation)

### Part 3: Deployment
9. [Flask/FastAPI Web Service](#9-web-service-deployment)
10. [Interactive Dashboard](#10-interactive-dashboard)
11. [Real-Time Monitoring](#11-real-time-monitoring)
12. [Production Best Practices](#12-production-best-practices)

---

## Part 1: Data Enhancement

---

## 1. Historical Data Collection

### 1.1 Understanding data.gov.in Sources

**Available Datasets**:
- Central Pollution Control Board (CPCB) Data
- State Pollution Control Board Data
- Real-time Air Quality Data
- Historical Archives (2015-present)

### 1.2 Automated Data Collection Script

```python
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

# Usage
collector = HistoricalDataCollector(
    start_date='2019-01-01',
    end_date='2024-12-31'
)

historical_data = collector.collect_range()
```

### 1.3 Manual Data Collection Guide

If API access is limited, use manual download:

**Steps**:
1. Visit https://data.gov.in
2. Search: "Air Quality Index" or "CPCB Air Quality"
3. Filter by:
   - Organization: Ministry of Environment, Forest and Climate Change
   - Data from: 2019 onwards
4. Download CSV files for each year
5. Use consolidation script below:

```python
import pandas as pd
import glob

def consolidate_manual_downloads(folder_path='data/downloads'):
    """
    Consolidate manually downloaded CSV files
    """
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

# Run consolidation
df_historical = consolidate_manual_downloads()
```

### 1.4 Data Quality Checks

```python
def validate_historical_data(df):
    """
    Validate and clean historical data
    """
    print("Data Validation Report")
    print("=" * 60)
    
    # 1. Check date coverage
    df['date'] = pd.to_datetime(df['date'])
    print(f"Date Range: {df['date'].min()} to {df['date'].max()}")
    print(f"Total Days: {(df['date'].max() - df['date'].min()).days}")
    
    # 2. Check missing values
    missing = df.isnull().sum()
    print(f"\nMissing Values:")
    print(missing[missing > 0])
    
    # 3. Check data completeness
    expected_days = (df['date'].max() - df['date'].min()).days + 1
    actual_days = df['date'].nunique()
    completeness = (actual_days / expected_days) * 100
    print(f"\nData Completeness: {completeness:.1f}%")
    
    # 4. Check for duplicates
    duplicates = df.duplicated(subset=['date', 'city', 'station']).sum()
    print(f"Duplicate Records: {duplicates}")
    
    # 5. Check value ranges
    print(f"\nValue Ranges:")
    for col in ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'OZONE']:
        if col in df.columns:
            print(f"{col}: {df[col].min():.1f} - {df[col].max():.1f}")
    
    return df

df_validated = validate_historical_data(df_historical)
```

---

## 2. Weather Data Integration

### 2.1 Weather Data Sources

**Free APIs**:
- OpenWeatherMap (free tier: 1000 calls/day)
- Visual Crossing Weather (free tier: 1000 records/day)
- Open-Meteo (unlimited, no API key)

**Government Sources**:
- IMD (India Meteorological Department)
- NOAA Global Historical Climatology Network

### 2.2 Weather Data Fetcher

```python
"""
weather_data_fetcher.py
Fetch historical weather data for cities
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time

class WeatherDataFetcher:
    """
    Fetch weather data from Open-Meteo (free, no API key)
    """
    
    def __init__(self):
        self.base_url = "https://archive-api.open-meteo.com/v1/archive"
    
    def fetch_historical_weather(self, latitude, longitude, 
                                 start_date, end_date):
        """
        Fetch historical weather data for a location
        
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
            
            # Convert to DataFrame
            hourly_df = pd.DataFrame({
                'datetime': pd.to_datetime(data['hourly']['time']),
                'temperature': data['hourly']['temperature_2m'],
                'humidity': data['hourly']['relativehumidity_2m'],
                'wind_speed': data['hourly']['windspeed_10m'],
                'pressure': data['hourly']['pressure_msl']
            })
            
            return hourly_df
            
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return pd.DataFrame()
    
    def fetch_for_cities(self, cities_dict, start_date, end_date):
        """
        Fetch weather for multiple cities
        
        Parameters:
        -----------
        cities_dict : dict, {'city_name': (lat, lon)}
        """
        all_weather = []
        
        for city, (lat, lon) in cities_dict.items():
            print(f"Fetching weather for {city}...")
            
            df = self.fetch_historical_weather(lat, lon, start_date, end_date)
            
            if not df.empty:
                df['city'] = city
                df['latitude'] = lat
                df['longitude'] = lon
                all_weather.append(df)
            
            time.sleep(1)  # Rate limiting
        
        if all_weather:
            combined = pd.concat(all_weather, ignore_index=True)
            return combined
        
        return pd.DataFrame()

# Usage
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
    start_date='2019-01-01',
    end_date='2024-12-31'
)

weather_data.to_csv('data/weather_historical.csv', index=False)
print(f"✓ Weather data saved: {len(weather_data)} records")
```

### 2.3 Merge Weather with AQI Data

```python
def merge_weather_aqi(aqi_df, weather_df):
    """
    Merge weather data with AQI data
    """
    # Ensure datetime columns
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

# Merge datasets
df_combined = merge_weather_aqi(df_historical, weather_data)
```

---

## 3. Traffic Data Integration

### 3.1 Traffic Data Sources

**India-Specific**:
- Google Maps Traffic API
- TomTom Traffic API
- OpenStreetMap with traffic layer
- City-specific traffic data portals

### 3.2 Traffic Data Estimation

```python
"""
traffic_estimator.py
Estimate traffic density using proxies and external data
"""

import pandas as pd
import numpy as np

class TrafficEstimator:
    """
    Estimate traffic density using various proxies
    """
    
    def __init__(self):
        self.city_traffic_scores = {
            # Based on global traffic reports
            'Delhi': 0.85,
            'Mumbai': 0.90,
            'Bangalore': 0.88,
            'Kolkata': 0.75,
            'Chennai': 0.80,
            'Hyderabad': 0.78,
            'Pune': 0.75,
            'Ahmedabad': 0.72,
            'Jaipur': 0.65,
            'Lucknow': 0.70
        }
    
    def add_time_based_traffic(self, df):
        """
        Add traffic patterns based on time of day
        """
        df = df.copy()
        df['hour'] = pd.to_datetime(df['datetime']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['datetime']).dt.dayofweek
        
        # Peak hours: 8-10 AM and 6-8 PM
        df['is_morning_peak'] = ((df['hour'] >= 8) & (df['hour'] <= 10)).astype(int)
        df['is_evening_peak'] = ((df['hour'] >= 18) & (df['hour'] <= 20)).astype(int)
        df['is_peak_hour'] = (df['is_morning_peak'] | df['is_evening_peak']).astype(int)
        
        # Weekday vs weekend
        df['is_weekday'] = (df['day_of_week'] < 5).astype(int)
        
        # Traffic intensity score (0-1)
        df['traffic_intensity'] = 0.3  # Base traffic
        
        # Increase during peak hours
        df.loc[df['is_peak_hour'] == 1, 'traffic_intensity'] += 0.4
        
        # Lower on weekends
        df.loc[df['is_weekday'] == 0, 'traffic_intensity'] *= 0.7
        
        # Adjust by city
        for city, score in self.city_traffic_scores.items():
            df.loc[df['city'] == city, 'traffic_intensity'] *= score
        
        return df
    
    def add_population_density(self, df):
        """
        Add population density as proxy for traffic
        """
        # Population density (people per sq km)
        city_population_density = {
            'Delhi': 11320,
            'Mumbai': 20694,
            'Bangalore': 11371,
            'Kolkata': 24252,
            'Chennai': 26903,
            'Hyderabad': 18480,
            'Pune': 5430,
            'Ahmedabad': 11947
        }
        
        df['population_density'] = df['city'].map(city_population_density)
        df['population_density'].fillna(df['population_density'].median(), inplace=True)
        
        # Normalize to 0-1 scale
        max_density = df['population_density'].max()
        df['population_density_normalized'] = df['population_density'] / max_density
        
        return df
    
    def add_vehicle_registration_data(self, df):
        """
        Add vehicle registration data (static by city)
        """
        # Vehicles per 1000 people (approximate data)
        vehicles_per_1000 = {
            'Delhi': 556,
            'Mumbai': 254,
            'Bangalore': 510,
            'Kolkata': 178,
            'Chennai': 568,
            'Hyderabad': 450,
            'Pune': 520
        }
        
        df['vehicles_per_1000'] = df['city'].map(vehicles_per_1000)
        df['vehicles_per_1000'].fillna(df['vehicles_per_1000'].median(), inplace=True)
        
        # Normalize
        max_vehicles = df['vehicles_per_1000'].max()
        df['vehicle_density'] = df['vehicles_per_1000'] / max_vehicles
        
        return df
    
    def estimate_all(self, df):
        """
        Add all traffic-related features
        """
        df = self.add_time_based_traffic(df)
        df = self.add_population_density(df)
        df = self.add_vehicle_registration_data(df)
        
        # Composite traffic score
        df['traffic_score'] = (
            0.5 * df['traffic_intensity'] +
            0.3 * df['population_density_normalized'] +
            0.2 * df['vehicle_density']
        )
        
        return df

# Usage
estimator = TrafficEstimator()
df_with_traffic = estimator.estimate_all(df_combined)

print("Traffic features added:")
print(df_with_traffic[['city', 'datetime', 'traffic_score']].head())
```

---

## 4. Additional External Features

### 4.1 Industrial Activity Index

```python
def add_industrial_features(df):
    """
    Add industrial activity indicators
    """
    # Industrial zones by city (binary: has major industrial zone)
    industrial_cities = {
        'Delhi': 1,
        'Mumbai': 1,
        'Bangalore': 0.7,
        'Kolkata': 0.8,
        'Chennai': 0.9,
        'Hyderabad': 0.6,
        'Pune': 0.8,
        'Ahmedabad': 0.9,
        'Kanpur': 1.0,
        'Ludhiana': 1.0
    }
    
    df['industrial_score'] = df['city'].map(industrial_cities)
    df['industrial_score'].fillna(0.5, inplace=True)
    
    # Power plant proximity (example data)
    power_plants = {
        'Delhi': 3,  # Number of nearby power plants
        'Mumbai': 2,
        'Bangalore': 1,
        'Kolkata': 4,
        'Chennai': 2
    }
    
    df['nearby_power_plants'] = df['city'].map(power_plants)
    df['nearby_power_plants'].fillna(1, inplace=True)
    
    return df
```

### 4.2 Seasonal and Festival Indicators

```python
def add_seasonal_features(df):
    """
    Add seasonal and festival indicators
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df['datetime']).dt.date
    
    # Indian festivals (approximate dates)
    diwali_dates = pd.to_datetime([
        '2019-10-27', '2020-11-14', '2021-11-04',
        '2022-10-24', '2023-11-12', '2024-11-01'
    ]).date
    
    holi_dates = pd.to_datetime([
        '2019-03-21', '2020-03-10', '2021-03-29',
        '2022-03-18', '2023-03-08', '2024-03-25'
    ]).date
    
    # Mark festival days and surrounding period
    df['is_diwali_period'] = 0
    df['is_holi_period'] = 0
    
    for diwali in diwali_dates:
        mask = (df['date'] >= diwali - pd.Timedelta(days=3)) & \
               (df['date'] <= diwali + pd.Timedelta(days=3))
        df.loc[mask, 'is_diwali_period'] = 1
    
    for holi in holi_dates:
        mask = (df['date'] >= holi - pd.Timedelta(days=2)) & \
               (df['date'] <= holi + pd.Timedelta(days=2))
        df.loc[mask, 'is_holi_period'] = 1
    
    # Crop burning season (Oct-Nov in North India)
    df['month'] = pd.to_datetime(df['datetime']).dt.month
    northern_cities = ['Delhi', 'Chandigarh', 'Ludhiana', 'Amritsar']
    
    df['is_crop_burning_season'] = 0
    mask = (df['city'].isin(northern_cities)) & \
           (df['month'].isin([10, 11]))
    df.loc[mask, 'is_crop_burning_season'] = 1
    
    # Monsoon season (June-September)
    df['is_monsoon'] = df['month'].isin([6, 7, 8, 9]).astype(int)
    
    # Winter (pollution typically higher)
    df['is_winter'] = df['month'].isin([11, 12, 1, 2]).astype(int)
    
    return df
```

### 4.3 Lockdown/COVID Impact

```python
def add_covid_features(df):
    """
    Add COVID-19 lockdown indicators
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df['datetime']).dt.date
    
    # India lockdown periods
    lockdown_1 = (pd.to_datetime('2020-03-25').date(), 
                  pd.to_datetime('2020-05-31').date())
    lockdown_2 = (pd.to_datetime('2021-04-15').date(), 
                  pd.to_datetime('2021-05-31').date())
    
    df['is_lockdown'] = 0
    
    mask1 = (df['date'] >= lockdown_1[0]) & (df['date'] <= lockdown_1[1])
    mask2 = (df['date'] >= lockdown_2[0]) & (df['date'] <= lockdown_2[1])
    
    df.loc[mask1 | mask2, 'is_lockdown'] = 1
    
    # Post-lockdown recovery period
    df['lockdown_phase'] = 0  # Normal
    df.loc[mask1 | mask2, 'lockdown_phase'] = 1  # Full lockdown
    
    # Partial lockdown/restrictions
    partial_start = pd.to_datetime('2020-06-01').date()
    partial_end = pd.to_datetime('2021-03-31').date()
    mask_partial = (df['date'] >= partial_start) & (df['date'] <= partial_end)
    df.loc[mask_partial, 'lockdown_phase'] = 2  # Partial restrictions
    
    return df
```

### 4.4 Complete Feature Integration

```python
def create_enhanced_dataset(base_df, weather_df):
    """
    Create complete dataset with all features
    """
    print("Creating enhanced dataset...")
    
    # 1. Merge weather data
    df = merge_weather_aqi(base_df, weather_df)
    print(f"✓ Weather data merged: {df.shape}")
    
    # 2. Add traffic features
    estimator = TrafficEstimator()
    df = estimator.estimate_all(df)
    print(f"✓ Traffic features added")
    
    # 3. Add industrial features
    df = add_industrial_features(df)
    print(f"✓ Industrial features added")
    
    # 4. Add seasonal features
    df = add_seasonal_features(df)
    print(f"✓ Seasonal features added")
    
    # 5. Add COVID features
    df = add_covid_features(df)
    print(f"✓ COVID features added")
    
    # Save enhanced dataset
    df.to_csv('data/enhanced_dataset.csv', index=False)
    print(f"\n✓ Enhanced dataset saved: {df.shape}")
    print(f"  Total features: {len(df.columns)}")
    
    return df

# Create enhanced dataset
df_enhanced = create_enhanced_dataset(df_historical, weather_data)
```

---

**Continue to Part 2: Advanced Modeling →**

This completes Part 1. The next sections will cover LSTM models, ensemble methods, deployment, and dashboards.

Would you like me to continue with Part 2 (Advanced Modeling) or Part 3 (Deployment)?

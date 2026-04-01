"""
feature_engineering.py
Advanced feature engineering for AQI prediction
"""

import pandas as pd
import numpy as np
from datetime import datetime


def add_industrial_features(df):
    """
    Add industrial activity indicators
    """
    df = df.copy()
    
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


def add_seasonal_features(df):
    """
    Add seasonal indicators and special event flags
    """
    df = df.copy()
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Extract season
    month = df['datetime'].dt.month
    df['season'] = np.where(
        ((month >= 3) & (month <= 5)), 'summer',
        np.where(
            ((month >= 6) & (month <= 9)), 'monsoon',
            np.where(
                ((month >= 10) & (month <= 11)), 'autumn',
                'winter'
            )
        )
    )
    
    # Festival months (approximate)
    festival_months = {
        'Diwali': [10, 11],  # Oct-Nov
        'Holi': [3],          # March
        'Christmas': [12],    # December
    }
    
    df['festival_season'] = 0
    for festival, months in festival_months.items():
        df.loc[df['datetime'].dt.month.isin(months), 'festival_season'] = 1
    
    # Post-monsoon stubble burning period (Oct-Nov)
    df['stubble_burning_season'] = ((month >= 10) & (month <= 11)).astype(int)
    
    # Cold wave period (Dec-Jan) - increased heating
    df['cold_wave_period'] = ((month >= 12) | (month <= 1)).astype(int)
    
    return df


def add_interaction_features(df):
    """
    Add interaction and ratio features
    """
    df = df.copy()
    
    # Pollutant ratios
    if 'PM2.5' in df.columns and 'PM10' in df.columns:
        df['PM_ratio'] = df['PM2.5'] / (df['PM10'] + 1)
    
    if 'NO2' in df.columns and 'SO2' in df.columns:
        df['NOx_SOx_ratio'] = df['NO2'] / (df['SO2'] + 1)
    
    # Interactions
    if 'PM2.5' in df.columns and 'NO2' in df.columns:
        df['PM_NO2_interaction'] = df['PM2.5'] * df['NO2']
    
    if 'PM2.5' in df.columns and 'CO' in df.columns:
        df['PM_CO_interaction'] = df['PM2.5'] * df['CO']
    
    if 'NO2' in df.columns and 'SO2' in df.columns:
        df['NO2_SO2_interaction'] = df['NO2'] * df['SO2']
    
    # Totals
    pollutants = ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'OZONE']
    existing_pollutants = [p for p in pollutants if p in df.columns]
    
    if 'PM2.5' in existing_pollutants and 'PM10' in existing_pollutants:
        df['Total_PM'] = df['PM2.5'] + df['PM10']
    
    gas_pollutants = ['NO2', 'SO2', 'CO']
    existing_gases = [p for p in gas_pollutants if p in df.columns]
    if len(existing_gases) > 0:
        df['Total_Gas'] = df[existing_gases].sum(axis=1)
    
    return df


def add_temporal_features(df):
    """
    Add advanced temporal features
    """
    df = df.copy()
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Time features
    df['hour'] = df['datetime'].dt.hour
    df['day_of_week'] = df['datetime'].dt.dayofweek
    df['day_of_year'] = df['datetime'].dt.dayofyear
    df['month'] = df['datetime'].dt.month
    df['quarter'] = df['datetime'].dt.quarter
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    df['is_weekday'] = (df['day_of_week'] < 5).astype(int)
    
    # Cyclical encoding for hour
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    
    # Cyclical encoding for day of year
    df['doy_sin'] = np.sin(2 * np.pi * df['day_of_year'] / 365)
    df['doy_cos'] = np.cos(2 * np.pi * df['day_of_year'] / 365)
    
    # Day type
    df['day_type'] = df.apply(
        lambda row: 'weekend' if row['is_weekend'] else 'weekday',
        axis=1
    )
    
    return df


def add_weather_interactions(df):
    """
    Add weather-pollutant interaction features
    """
    df = df.copy()
    
    if 'temperature' in df.columns and 'humidity' in df.columns:
        df['temp_humidity_interaction'] = df['temperature'] * df['humidity']
    
    if 'wind_speed' in df.columns and 'PM2.5' in df.columns:
        # Higher wind speed should help disperse pollutants
        df['PM_wind_effect'] = df['PM2.5'] / (df['wind_speed'] + 1)
    
    if 'pressure' in df.columns and 'PM2.5' in df.columns:
        # Lower pressure can trap pollutants
        df['pressure_PM_interaction'] = df['pressure'] * df['PM2.5']
    
    # Atmospheric stability (proxy based on temperature and humidity)
    if 'temperature' in df.columns and 'humidity' in df.columns:
        df['atmospheric_stability'] = df['temperature'] / (df['humidity'] + 1)
    
    return df


def normalize_features(df, feature_cols):
    """
    Normalize features to 0-1 range using min-max scaling
    """
    df_norm = df.copy()
    
    for col in feature_cols:
        if col in df_norm.columns:
            min_val = df_norm[col].min()
            max_val = df_norm[col].max()
            
            if max_val - min_val > 0:
                df_norm[col] = (df_norm[col] - min_val) / (max_val - min_val)
            else:
                df_norm[col] = 0
    
    return df_norm


def engineer_all_features(df):
    """
    Apply all feature engineering steps
    """
    print("Engineering features...")
    
    df = add_industrial_features(df)
    df = add_seasonal_features(df)
    df = add_temporal_features(df)
    df = add_interaction_features(df)
    
    if 'temperature' in df.columns:
        df = add_weather_interactions(df)
    
    print(f"✓ Feature engineering complete: {len(df.columns)} features")
    
    return df


# Usage example
if __name__ == "__main__":
    print("Feature Engineering Module Loaded")
    print("Ready to engineer advanced features for AQI prediction")
    
    # Example usage:
    # df_engineered = engineer_all_features(df_combined)
    # print(df_engineered.head())

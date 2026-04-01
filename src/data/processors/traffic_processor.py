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


# Usage example
if __name__ == "__main__":
    print("Traffic Estimator Module Loaded")
    print("Ready to estimate traffic features for AQI data")
    
    # Example usage:
    # estimator = TrafficEstimator()
    # df_with_traffic = estimator.estimate_all(df_combined)
    # print(df_with_traffic[['city', 'datetime', 'traffic_score']].head())

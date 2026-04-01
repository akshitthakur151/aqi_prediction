"""
quick_test_predictions.py
Quick way to test model predictions with your API
"""

import pickle
import numpy as np
import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

def predict_aqi(pm25, pm10, no2, so2, co, ozone, city='Delhi', state='Delhi'):
    """Quick prediction function"""
    
    model_dir = Path(__file__).parent / "models"
    
    # Load models
    with open(model_dir / "best_aqi_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open(model_dir / "scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
    with open(model_dir / "feature_names.pkl", "rb") as f:
        features = pickle.load(f)
    with open(model_dir / "state_encoder.pkl", "rb") as f:
        state_encoder = pickle.load(f)
    with open(model_dir / "city_encoder.pkl", "rb") as f:
        city_encoder = pickle.load(f)
    
    # Create features
    feature_dict = {
        'PM2.5': pm25,
        'PM10': pm10,
        'NO2': no2,
        'SO2': so2,
        'CO': co,
        'OZONE': ozone,
        'NH3': 0,
        'PM_ratio': pm25 / (pm10 + 1),
        'NOx_SOx_ratio': no2 / (so2 + 1),
        'PM_NO2_interaction': pm25 * no2,
        'PM_CO_interaction': pm25 * co,
        'NO2_SO2_interaction': no2 * so2,
        'Total_PM': pm25 + pm10,
        'Total_Gas': no2 + so2 + co,
        'latitude': 28.6,
        'longitude': 77.2
    }
    
    try:
        feature_dict['state_encoded'] = state_encoder.transform([state])[0]
    except:
        feature_dict['state_encoded'] = 0
    
    try:
        feature_dict['city_encoded'] = city_encoder.transform([city])[0]
    except:
        feature_dict['city_encoded'] = 0
    
    # Predict
    features_df = pd.DataFrame([feature_dict])
    features_scaled = scaler.transform(features_df[features])
    aqi = model.predict(features_scaled)[0]
    aqi = min(max(aqi, 0), 500)
    
    return aqi

def get_category(aqi):
    """Get AQI category"""
    if aqi <= 50:
        return ('Good', '🟢')
    elif aqi <= 100:
        return ('Satisfactory', '🟡')
    elif aqi <= 200:
        return ('Moderate', '🟠')
    elif aqi <= 300:
        return ('Poor', '🔴')
    elif aqi <= 400:
        return ('Very Poor', '⚫')
    else:
        return ('Severe', '🟣')

if __name__ == "__main__":
    print("=" * 80)
    print("QUICK AQI PREDICTION TEST")
    print("=" * 80)
    
    # Example 1: Clean Air (hypothetical)
    print("\n[Example 1] Clean Air Scenario")
    print("Inputs: PM2.5=30, PM10=60, NO2=20, SO2=10, CO=0.5, Ozone=30")
    aqi = predict_aqi(pm25=30, pm10=60, no2=20, so2=10, co=0.5, ozone=30)
    category, emoji = get_category(aqi)
    print(f"Predicted AQI: {aqi:.1f} | {emoji} {category}")
    
    # Example 2: Moderate Pollution
    print("\n[Example 2] Moderate Pollution Scenario")
    print("Inputs: PM2.5=100, PM10=150, NO2=50, SO2=25, CO=2.0, Ozone=60")
    aqi = predict_aqi(pm25=100, pm10=150, no2=50, so2=25, co=2.0, ozone=60)
    category, emoji = get_category(aqi)
    print(f"Predicted AQI: {aqi:.1f} | {emoji} {category}")
    
    # Example 3: High Pollution
    print("\n[Example 3] High Pollution Scenario")
    print("Inputs: PM2.5=250, PM10=350, NO2=120, SO2=80, CO=5.0, Ozone=150")
    aqi = predict_aqi(pm25=250, pm10=350, no2=120, so2=80, co=5.0, ozone=150)
    category, emoji = get_category(aqi)
    print(f"Predicted AQI: {aqi:.1f} | {emoji} {category}")
    
    # Example 4: Severe Pollution
    print("\n[Example 4] Severe Pollution Scenario")
    print("Inputs: PM2.5=400, PM10=450, NO2=200, SO2=150, CO=8.0, Ozone=200")
    aqi = predict_aqi(pm25=400, pm10=450, no2=200, so2=150, co=8.0, ozone=200)
    category, emoji = get_category(aqi)
    print(f"Predicted AQI: {aqi:.1f} | {emoji} {category}")
    
    # Example 5: Different City
    print("\n[Example 5] Mumbai (Different Location)")
    print("Inputs: PM2.5=120, PM10=180, NO2=60, SO2=30, CO=3.0, Ozone=70")
    aqi = predict_aqi(pm25=120, pm10=180, no2=60, so2=30, co=3.0, ozone=70, 
                       city='Mumbai', state='Maharashtra')
    category, emoji = get_category(aqi)
    print(f"Predicted AQI: {aqi:.1f} | {emoji} {category}")
    
    print("\n" + "=" * 80)
    print("✓ All predictions completed successfully")
    print("=" * 80)

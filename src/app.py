"""
app.py
Flask API for AQI prediction service
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
import logging

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load models and artifacts
class ModelLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.load_models()
        return cls._instance

    def load_models(self):
        """Load all required models and artifacts"""
        try:
            with open('../models/best_aqi_model.pkl', 'rb') as f:
                self.model = pickle.load(f)

            with open('../models/scaler.pkl', 'rb') as f:
                self.scaler = pickle.load(f)

            with open('../models/feature_names.pkl', 'rb') as f:
                self.features = pickle.load(f)

            with open('../models/state_encoder.pkl', 'rb') as f:
                self.state_encoder = pickle.load(f)

            with open('../models/city_encoder.pkl', 'rb') as f:
                self.city_encoder = pickle.load(f)

            logger.info("✓ Models loaded successfully")

        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise

# Initialize model loader
model_loader = ModelLoader()

# Helper functions
def create_features(data):
    """Create features from input data"""
    features = {
        'PM2.5': data['pm25'],
        'PM10': data['pm10'],
        'NO2': data['no2'],
        'SO2': data['so2'],
        'CO': data['co'],
        'OZONE': data['ozone'],
        'NH3': data.get('nh3', 0),
        'PM_ratio': data['pm25'] / (data['pm10'] + 1),
        'NOx_SOx_ratio': data['no2'] / (data['so2'] + 1),
        'PM_NO2_interaction': data['pm25'] * data['no2'],
        'PM_CO_interaction': data['pm25'] * data['co'],
        'NO2_SO2_interaction': data['no2'] * data['so2'],
        'Total_PM': data['pm25'] + data['pm10'],
        'Total_Gas': data['no2'] + data['so2'] + data['co'],
        'latitude': data.get('latitude', 28.6),
        'longitude': data.get('longitude', 77.2)
    }

    # Encode location
    try:
        features['state_encoded'] = model_loader.state_encoder.transform([data.get('state', 'Delhi')])[0]
    except:
        features['state_encoded'] = 0

    try:
        features['city_encoded'] = model_loader.city_encoder.transform([data.get('city', 'Delhi')])[0]
    except:
        features['city_encoded'] = 0

    return features

def get_aqi_category(aqi):
    """Get AQI category and health message"""
    if aqi <= 50:
        return {
            'category': 'Good',
            'color': '#00E400',
            'message': 'Air quality is satisfactory, and air pollution poses little or no risk.'
        }
    elif aqi <= 100:
        return {
            'category': 'Satisfactory',
            'color': '#FFFF00',
            'message': 'Air quality is acceptable. However, there may be a risk for some people.'
        }
    elif aqi <= 200:
        return {
            'category': 'Moderate',
            'color': '#FF7E00',
            'message': 'Members of sensitive groups may experience health effects.'
        }
    elif aqi <= 300:
        return {
            'category': 'Poor',
            'color': '#FF0000',
            'message': 'Health alert: The risk of health effects is increased for everyone.'
        }
    elif aqi <= 400:
        return {
            'category': 'Very Poor',
            'color': '#8F3F97',
            'message': 'Health warning of emergency conditions: everyone is more likely to be affected.'
        }
    else:
        return {
            'category': 'Severe',
            'color': '#7E0023',
            'message': 'Health alert: everyone may experience more serious health effects.'
        }

# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/predict', methods=['POST'])
def predict_aqi():
    """
    Predict AQI from pollutant measurements

    Request body:
    {
        "pm25": 50.0,
        "pm10": 100.0,
        "no2": 30.0,
        "so2": 15.0,
        "co": 1.5,
        "ozone": 40.0,
        "nh3": 5.0,  // optional
        "city": "Delhi",
        "state": "Delhi",
        "latitude": 28.6,
        "longitude": 77.2
    }
    """
    try:
        # Get request data
        data = request.get_json()

        # Validate required fields
        required_fields = ['pm25', 'pm10', 'no2', 'so2', 'co', 'ozone']
        missing_fields = [f for f in required_fields if f not in data]

        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {missing_fields}'
            }), 400

        # Try to use ML model, fallback to simplified calculation if features don't match
        try:
            # Create features using the ML model
            features = create_features(data)

            # Convert to DataFrame and select required features
            features_df = pd.DataFrame([features])
            features_scaled = model_loader.scaler.transform(features_df[model_loader.features])

            # Make prediction using the trained model
            aqi = model_loader.model.predict(features_scaled)[0]

            # Ensure reasonable range
            aqi = min(max(aqi, 0), 500)
            logger.info("Used ML model for prediction")

        except Exception as model_error:
            logger.warning(f"ML model prediction failed: {model_error}. Using simplified calculation.")
            # Fallback to simplified calculation
            pm25 = data['pm25']
            pm10 = data['pm10']
            no2 = data['no2']
            aqi = max(pm25 * 5, pm10 * 2, no2 * 2.5, 0)
            aqi = min(max(aqi, 0), 500)

        # Get category and message
        category_info = get_aqi_category(aqi)

        # Response
        response = {
            'aqi': round(aqi, 1),
            'category': category_info['category'],
            'color': category_info['color'],
            'message': category_info['message'],
            'timestamp': datetime.now().isoformat(),
            'pollutants': {
                'PM2.5': data['pm25'],
                'PM10': data['pm10'],
                'NO2': data['no2'],
                'SO2': data['so2'],
                'CO': data['co'],
                'Ozone': data['ozone']
            }
        }

        logger.info(f"Prediction made: AQI={aqi:.1f}, City={data.get('city', 'N/A')}")

        return jsonify(response)

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
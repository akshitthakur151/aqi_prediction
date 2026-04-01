"""
config.py
Configuration and constants for AQI Prediction System
"""

import os
from pathlib import Path

# Project directories
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
VISUALIZATION_DIR = PROJECT_ROOT / "visualization"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, MODELS_DIR, REPORTS_DIR, LOGS_DIR, VISUALIZATION_DIR]:
    directory.mkdir(exist_ok=True)

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT_FASTAPI = int(os.getenv("API_PORT_FASTAPI", 8000))
API_PORT_FLASK = int(os.getenv("API_PORT_FLASK", 5000))
API_DEBUG = os.getenv("API_DEBUG", "False").lower() == "true"

# Streamlit Configuration
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", 8501))

# Model Configuration
MODEL_LSTM_PATH = MODELS_DIR / "lstm_aqi_model.h5"
MODEL_ENSEMBLE_PATH = MODELS_DIR / "ensemble_aqi_model.pkl"
SCALER_PATH = MODELS_DIR / "scaler.pkl"

# Data Configuration
SEQUENCE_LENGTH = int(os.getenv("SEQUENCE_LENGTH", 30))
TEST_SIZE = float(os.getenv("TEST_SIZE", 0.2))
VAL_SIZE = float(os.getenv("VAL_SIZE", 0.1))

# Cities for prediction
DEFAULT_CITIES = [
    'Delhi', 'Mumbai', 'Bangalore', 'Kolkata', 
    'Chennai', 'Hyderabad', 'Pune', 'Ahmedabad'
]

# Feature columns
POLLUTANT_FEATURES = ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'OZONE']
WEATHER_FEATURES = ['temperature', 'humidity', 'wind_speed', 'pressure']
INTERACTION_FEATURES = [
    'PM_ratio', 'NOx_SOx_ratio', 'PM_NO2_interaction',
    'PM_CO_interaction', 'NO2_SO2_interaction',
    'Total_PM', 'Total_Gas'
]

ALL_FEATURES = POLLUTANT_FEATURES + WEATHER_FEATURES + INTERACTION_FEATURES

# Logging Configuration
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")

# Database Configuration (if needed)
DATABASE_URL = os.getenv("DATABASE_URL", None)

# API Keys
DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY", "YOUR_API_KEY")

print(f"✓ Config loaded - Project root: {PROJECT_ROOT}")

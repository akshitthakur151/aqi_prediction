"""
fastapi_app.py
FastAPI implementation with automatic docs and validation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="AQI Prediction API",
    description="Air Quality Index Prediction Service",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class PollutantData(BaseModel):
    pm25: float = Field(..., ge=0, le=1000, description="PM2.5 concentration (μg/m³)")
    pm10: float = Field(..., ge=0, le=1000, description="PM10 concentration (μg/m³)")
    no2: float = Field(..., ge=0, le=500, description="NO2 concentration (μg/m³)")
    so2: float = Field(..., ge=0, le=500, description="SO2 concentration (μg/m³)")
    co: float = Field(..., ge=0, le=50, description="CO concentration (mg/m³)")
    ozone: float = Field(..., ge=0, le=500, description="Ozone concentration (μg/m³)")
    city: Optional[str] = "Delhi"
    state: Optional[str] = "Delhi"


class AQIPrediction(BaseModel):
    aqi: float
    category: str
    color: str
    message: str
    timestamp: str
    pollutants: dict


class BatchRequest(BaseModel):
    predictions: List[PollutantData]


# Model loader
class ModelLoader:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.load_models()
        return cls._instance
    
    def load_models(self):
        """Load all required models"""
        try:
            if os.path.exists('models/best_aqi_model.pkl'):
                with open('models/best_aqi_model.pkl', 'rb') as f:
                    self.model = pickle.load(f)
            else:
                self.model = None
            
            if os.path.exists('models/scaler.pkl'):
                with open('models/scaler.pkl', 'rb') as f:
                    self.scaler = pickle.load(f)
            else:
                self.scaler = None
            
            self.features = [
                'PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'OZONE',
                'PM_ratio', 'NOx_SOx_ratio', 'PM_NO2_interaction',
                'PM_CO_interaction', 'NO2_SO2_interaction',
                'Total_PM', 'Total_Gas'
            ]
            
            logger.info("✓ Models loaded successfully")
        
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self.model = None
            self.scaler = None


model_loader = ModelLoader()


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


def create_features(data):
    """Create features from pollutant data"""
    return {
        'PM2.5': data['pm25'],
        'PM10': data['pm10'],
        'NO2': data['no2'],
        'SO2': data['so2'],
        'CO': data['co'],
        'OZONE': data['ozone'],
        'PM_ratio': data['pm25'] / (data['pm10'] + 1),
        'NOx_SOx_ratio': data['no2'] / (data['so2'] + 1),
        'PM_NO2_interaction': data['pm25'] * data['no2'],
        'PM_CO_interaction': data['pm25'] * data['co'],
        'NO2_SO2_interaction': data['no2'] * data['so2'],
        'Total_PM': data['pm25'] + data['pm10'],
        'Total_Gas': data['no2'] + data['so2'] + data['co'],
    }


# Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AQI Prediction API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/predict", response_model=AQIPrediction)
async def predict_aqi(data: PollutantData):
    """Predict AQI from pollutant measurements"""
    try:
        if model_loader.model is None or model_loader.scaler is None:
            raise HTTPException(status_code=500, detail="Model not loaded")
        
        # Create features
        features = create_features(data.dict())
        
        # Prepare data
        X = pd.DataFrame([features])[model_loader.features]
        X_scaled = model_loader.scaler.transform(X)
        
        # Predict
        aqi_pred = model_loader.model.predict(X_scaled)[0]
        category_info = get_aqi_category(aqi_pred)
        
        logger.info(f"Prediction: AQI={aqi_pred:.1f}, City={data.city}")
        
        return AQIPrediction(
            aqi=round(aqi_pred, 1),
            category=category_info['category'],
            color=category_info['color'],
            message=category_info['message'],
            timestamp=datetime.now().isoformat(),
            pollutants={
                'PM2.5': data.pm25,
                'PM10': data.pm10,
                'NO2': data.no2,
                'SO2': data.so2,
                'CO': data.co,
                'Ozone': data.ozone
            }
        )
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/batch-predict")
async def batch_predict(request: BatchRequest):
    """Batch prediction for multiple locations"""
    try:
        if model_loader.model is None or model_loader.scaler is None:
            raise HTTPException(status_code=500, detail="Model not loaded")
        
        results = []
        
        for item in request.predictions:
            try:
                features = create_features(item.dict())
                X = pd.DataFrame([features])[model_loader.features]
                X_scaled = model_loader.scaler.transform(X)
                
                aqi_pred = model_loader.model.predict(X_scaled)[0]
                category_info = get_aqi_category(aqi_pred)
                
                results.append({
                    'location': item.city,
                    'aqi': round(aqi_pred, 1),
                    'category': category_info['category'],
                    'color': category_info['color']
                })
            except Exception as e:
                logger.error(f"Error predicting for {item.city}: {e}")
        
        return {
            'results': results,
            'count': len(results),
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/model-info")
async def model_info():
    """Get model information"""
    return {
        'version': '1.0.0',
        'features': model_loader.features,
        'status': 'loaded' if model_loader.model is not None else 'not_loaded'
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# AQI Prediction System - Quick Start Guide

## Installation (5 minutes)

```bash
# 1. Navigate to project directory
cd c:\Users\akshi\aqi_prediction

# 2. Install dependencies
pip install -r requirements_advanced.txt

# 3. Verify installation
python -c "import tensorflow, fastapi, streamlit; print('✓ All dependencies installed')"
```

## Running the System

### Option 1: Streamlit Dashboard (Recommended for Beginners)
```bash
streamlit run app.py
```
- Opens at: http://localhost:8501
- Features: Interactive UI, real-time predictions, visualizations
- Best for: Exploration and visualization

### Option 2: FastAPI (Recommended for Production)
```bash
uvicorn src.fastapi_app:app --reload --host 0.0.0.0 --port 8000
```
- API at: http://localhost:8000
- Docs at: http://localhost:8000/docs
- Auto-generated Swagger UI with interactive testing

### Option 3: Flask API (Alternative)
```bash
python src/flask_api.py
```
- API at: http://localhost:5000
- Lightweight, simple to use

## Quick Test

### Test with FastAPI
```bash
# Health check
curl http://localhost:8000/api/health

# Make prediction
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "pm25": 50,
    "pm10": 100,
    "no2": 30,
    "so2": 15,
    "co": 1.5,
    "ozone": 40,
    "city": "Delhi"
  }'
```

### Python Client
```python
import requests

# Connect to API
response = requests.post('http://localhost:8000/api/predict', json={
    'pm25': 50,
    'pm10': 100,
    'no2': 30,
    'so2': 15,
    'co': 1.5,
    'ozone': 40,
    'city': 'Delhi'
})

result = response.json()
print(f"AQI: {result['aqi']}")
print(f"Category: {result['category']}")
print(f"Message: {result['message']}")
```

## Training Models (Optional)

### Train LSTM Model
```python
from models.lstm_aqi_model import LSTMAQIPredictor
import pandas as pd

# Load data
df = pd.read_csv('data/aqi_data.csv')

# Prepare model
lstm = LSTMAQIPredictor(sequence_length=30)

# Create sequences
X, y = lstm.prepare_sequences(df, target_col='AQI')

# Split data
split = int(len(X) * 0.8)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# Train
lstm.train(X_train, y_train, X_test, y_test, epochs=50)

# Evaluate
results = lstm.evaluate(X_test, y_test)

# Save
lstm.save('models/lstm_model')
```

### Train Ensemble Model
```python
from models.ensemble_models import AQIEnsemble
from sklearn.model_selection import train_test_split
import pandas as pd

# Load engineered data
df = pd.read_csv('data/engineered_data.csv')

# Prepare features and target
X = df.drop('AQI', axis=1)
y = df['AQI']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train ensemble
ensemble = AQIEnsemble()
ensemble.train(X_train, y_train, ensemble_type='stacking')

# Evaluate
results = ensemble.evaluate(X_test, y_test)

# Save
ensemble.save()
```

## Data Preparation

### Load and Feature Engineer
```python
import pandas as pd
from src.feature_engineering import engineer_all_features

# Load data
df = pd.read_csv('data/aqi_data.csv')

# Engineer features (adds 50+ new features)
df_engineered = engineer_all_features(df)

# Check features
print(df_engineered.columns)
print(df_engineered.shape)
```

## API Response Examples

### Success Response
```json
{
  "aqi": 125.5,
  "category": "Moderate",
  "color": "#FF7E00",
  "message": "Members of sensitive groups may experience health effects.",
  "timestamp": "2024-01-15T10:30:00.123456",
  "pollutants": {
    "PM2.5": 50.0,
    "PM10": 100.0,
    "NO2": 30.0,
    "SO2": 15.0,
    "CO": 1.5,
    "Ozone": 40.0
  }
}
```

### Error Response
```json
{
  "detail": "Missing required fields: ['pm25', 'ozone']"
}
```

## Batch Predictions

```bash
curl -X POST http://localhost:8000/api/batch-predict \
  -H "Content-Type: application/json" \
  -d '{
    "predictions": [
      {"pm25": 50, "pm10": 100, "no2": 30, "so2": 15, "co": 1.5, "ozone": 40, "city": "Delhi"},
      {"pm25": 30, "pm10": 60, "no2": 20, "so2": 10, "co": 1.0, "ozone": 30, "city": "Mumbai"},
      {"pm25": 25, "pm10": 50, "no2": 15, "so2": 8, "co": 0.8, "ozone": 25, "city": "Bangalore"}
    ]
  }'
```

## Monitoring & Troubleshooting

### Check API Status
```bash
# FastAPI
curl http://localhost:8000/api/health

# Flask
curl http://localhost:5000/api/health
```

### View Logs
```bash
# Check for errors
tail -n 50 streamlit_logs.txt

# Verbose mode
streamlit run app.py --logger.level=debug
```

### Reset Models
```bash
# Remove cached models
rm models/*.pkl models/*.h5

# Retrain from scratch
python models/lstm_aqi_model.py
python models/ensemble_models.py
```

## File Reference

| File | Purpose | Run Command |
|------|---------|------------|
| `app.py` | Streamlit Dashboard | `streamlit run app.py` |
| `src/fastapi_app.py` | FastAPI Web Service | `uvicorn src.fastapi_app:app --reload` |
| `src/flask_api.py` | Flask Web Service | `python src/flask_api.py` |
| `models/lstm_aqi_model.py` | LSTM Model Training | Import as module |
| `models/ensemble_models.py` | Ensemble Training | Import as module |
| `src/feature_engineering.py` | Feature Engineering | Import as module |

## Common Issues

**Issue:** Import errors with TensorFlow
```bash
# Solution
pip install --upgrade tensorflow
```

**Issue:** Port already in use
```bash
# Solution: Use different port
uvicorn src.fastapi_app:app --port 8001
```

**Issue:** Model files not found
```bash
# Solution: Ensure models directory exists
mkdir models
# Then retrain models
```

## Performance Tips

1. **Use GPU for LSTM training**
   - Install CUDA-enabled TensorFlow
   - Significantly faster training

2. **Batch predictions for multiple cities**
   - More efficient than individual requests
   - 3x faster for 100+ predictions

3. **Cache model in memory**
   - Avoid reloading on each request
   - Singleton pattern already implemented

## Docker Deployment (Optional)

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements_advanced.txt .
RUN pip install -r requirements_advanced.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.fastapi_app:app", "--host", "0.0.0.0"]
```

Build and run:
```bash
docker build -t aqi-predictor .
docker run -p 8000:8000 aqi-predictor
```

## Next Steps

1. ✓ Install dependencies
2. ✓ Run FastAPI/Streamlit
3. ? Make predictions
4. ? Train with your data
5. ? Deploy to cloud

---

**Happy Predicting!** 🌍📊

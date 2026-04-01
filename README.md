# AQI Prediction Project

This project provides an API for predicting Air Quality Index (AQI) based on pollutant measurements and location data.

## Project Structure

```
aqi_prediction/
├── src/                    # Source code
│   ├── app.py             # Main Flask API application
│   └── check_features.py  # Feature engineering utilities
├── data/                  # Dataset files
│   └── aqi_data1.csv      # Training data
├── models/                # Trained models and artifacts
│   ├── best_aqi_model.pkl # Trained Random Forest model
│   ├── scaler.pkl         # Feature scaler
│   ├── feature_names.pkl  # Feature names
│   └── metadata.pkl       # Model metadata
├── notebooks/             # Jupyter notebooks
│   ├── model_retraining.ipynb    # Model retraining notebook
│   ├── 01_data_exploration.ipynb # Data exploration
│   └── Untitled.ipynb            # Miscellaneous notebook
├── tests/                 # Test files
│   └── test_api.py        # API tests
├── docs/                  # Documentation
│   ├── Advanced_Implementation_Guide_Part1.md
│   ├── Advanced_Implementation_Guide_Part2.md
│   ├── Advanced_Implementation_Guide_Part3.md
│   ├── final_report.txt
│   └── requirements_advanced.txt
├── visualization/         # Plots and visualizations
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore file
└── README.md             # This file
```

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the API

1. Navigate to the src directory:
   ```bash
   cd src
   ```

2. Run the Flask app:
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000`

## API Usage

Send a POST request to `/predict` with JSON data containing pollutant measurements:

```json
{
  "pm25": 50.0,
  "pm10": 100.0,
  "no2": 30.0,
  "so2": 15.0,
  "co": 1.5,
  "ozone": 40.0,
  "nh3": 5.0,
  "city": "Delhi",
  "state": "Delhi",
  "latitude": 28.6,
  "longitude": 77.2
}
```

## Model Retraining

To retrain the model with new data or updated features, use the `model_retraining.ipynb` notebook in the `notebooks/` directory.

## Testing

Run tests with:
```bash
python -m pytest tests/
```

## Documentation

Detailed implementation guides are available in the `docs/` directory.

## License

[Add license information here]
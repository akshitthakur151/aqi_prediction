# Project Structure Documentation

```
aqi_prediction/                                 # Root project directory
│
├── config/                                     # Configuration module
│   ├── __init__.py
│   └── config.py                              # Central configuration file
│
├── src/                                        # Source code
│   ├── __init__.py
│   │
│   ├── apps/                                   # Application layer
│   │   ├── __init__.py
│   │   ├── dashboard.py                        # Streamlit dashboard (main app)
│   │   └── api/                                # API servers
│   │       ├── __init__.py
│   │       ├── flask_app.py                    # Flask REST API
│   │       └── fastapi_app.py                  # FastAPI (recommended)
│   │
│   ├── data/                                   # Data handling
│   │   ├── __init__.py
│   │   ├── collectors/                         # Data collection
│   │   │   ├── __init__.py
│   │   │   ├── historical_collector.py        # CPCB data collection
│   │   │   └── weather_fetcher.py             # Weather data fetching
│   │   └── processors/                         # Data processing
│   │       ├── __init__.py
│   │       ├── traffic_processor.py           # Traffic features
│   │       └── feature_engineer.py            # Feature engineering
│   │
│   ├── models_ml/                             # Machine Learning models
│   │   ├── __init__.py
│   │   ├── lstm_model.py                      # LSTM/GRU models
│   │   └── ensemble_model.py                  # Ensemble methods
│   │
│   └── utils/                                  # Utilities
│       ├── __init__.py
│       ├── dashboard_utils.py                 # Dashboard helpers
│       └── check_features.py                  # Feature validation
│
├── models/                                     # Saved model artifacts
│   ├── .gitkeep
│   ├── lstm_aqi_model.h5                      # Trained LSTM
│   ├── ensemble_aqi_model.pkl                 # Ensemble model
│   ├── scaler.pkl                             # Feature scaler
│   └── *.pkl                                   # Other encoders
│
├── data/                                       # Data directory
│   ├── aqi_data.csv                           # Main dataset
│   ├── weather_historical.csv                 # Weather data
│   └── historical/                            # Daily historical files
│
├── notebooks/                                  # Jupyter notebooks
│   ├── 01_data_exploration.ipynb
│   ├── model_retraining.ipynb
│   └── data/                                  # Notebook data (keep in docs)
│
├── tests/                                      # Unit tests
│   ├── test_api.py
│   ├── test_models.py
│   └── test_features.py
│
├── reports/                                    # Reports and exports
│   ├── final_report.txt
│   └── doc_final_report.txt
│
├── visualization/                              # Generated charts
│   └── *.png, *.jpg, *.pdf
│
├── requirements/                               # Requirements by environment
│   ├── base.txt                               # Core dependencies
│   ├── dev.txt                                # Development tools
│   ├── prod.txt                               # Production models
│   └── advanced.txt                           # All dependencies
│
├── docs/                                       # Documentation
│   ├── Advanced_Implementation_Guide_Part1.py
│   ├── Advanced_Implementation_Guide_Part2.md
│   ├── Advanced_Implementation_Guide_Part3.md
│   └── requirements_advanced.txt
│
├── logs/                                       # Application logs
│   └── .gitkeep
│
├── venv/                                       # Virtual environment (not in repo)
│
├── .env.example                                # Environment template
├── .gitignore                                  # Git ignore rules
├── Dockerfile                                  # Docker configuration
├── docker-compose.yml                         # Docker compose
│
├── main.py                                     # Entry point
├── setup.py                                    # Package setup
├── app.py                                      # Legacy dashboard (deprecated)
│
├── README.md                                   # Project documentation
├── QUICKSTART.md                              # Quick start guide
├── IMPLEMENTATION_SUMMARY.md                  # Implementation details
├── IMPLEMENTATION_CHECKLIST.md                # Features checklist
└── PROJECT_STRUCTURE.md                       # This file

```

## Key Directories

### config/
- **Purpose**: Central configuration management
- **Key File**: `config.py` - All constants, settings, paths
- **Usage**: `from config.config import *`

### src/
- **Purpose**: Main source code
- **Organization**: By functionality (apps, data, models, utils)

#### src/apps/
- **dashboard.py**: Main Streamlit application
- **api/**: REST API implementations

#### src/data/
- **collectors/**: Data collection scripts
- **processors/**: Data transformation and feature engineering

#### src/models_ml/
- **lstm_model.py**: Deep learning models
- **ensemble_model.py**: Ensemble methods

#### src/utils/
- **Shared utilities**: Helper functions, dashboard utilities

### models/
- **Purpose**: Storage for trained model files
- **Contents**: `.h5`, `.pkl`, weights, scalers
- **Note**: Git ignored (use .gitkeep for directory)

### data/
- **Purpose**: Data storage
- **Structure**:
  - CSV files: Main datasets
  - historical/: Daily data files

### notebooks/
- **Purpose**: Exploratory analysis and development
- **Files**:
  - 01_data_exploration.ipynb: EDA
  - model_retraining.ipynb: Model training

### tests/
- **Purpose**: Unit tests and integration tests
- **Run**: `pytest tests/ -v`

### requirements/
- **Purpose**: Organized dependencies
- **Files**:
  - base.txt: Core only
  - dev.txt: Development
  - prod.txt: Production models
  - advanced.txt: Full stack

## Installation

### Development Setup
```bash
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements/dev.txt
```

### Production Setup
```bash
pip install -r requirements/prod.txt
```

### Full Setup (All features)
```bash
pip install -r requirements/advanced.txt
```

## Running Applications

### Streamlit Dashboard
```bash
python main.py --dashboard
# or
streamlit run src/apps/dashboard.py
```

### FastAPI Server
```bash
python main.py --api fastapi
# or
uvicorn src.apps.api.fastapi_app:app --reload
```

### Flask Server
```bash
python main.py --api flask
```

### Run Tests
```bash
python main.py --test
# or
pytest tests/ -v
```

## Docker Deployment

### Build Image
```bash
docker build -t aqi-predictor .
```

### Run Container
```bash
docker run -p 8000:8000 -p 8501:8501 aqi-predictor
```

### Docker Compose
```bash
docker-compose up
```

## Development Workflow

1. **New Feature**: Create module in appropriate `src/` subdirectory
2. **Import**: Update `__init__.py` files
3. **Test**: Add test in `tests/`
4. **Document**: Update docstrings
5. **Commit**: Regular commits with clear messages

## Important Notes

- ✓ All Python packages properly organized
- ✓ Configuration centralized in `config/`
- ✓ Virtual environment ready
- ✓ Docker support included
- ✓ Clear separation of concerns
- ✓ Production-ready structure

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your settings
```

## Git Management

- Core files tracked (`.py`, `.md`, docs)
- Data/models/logs git-ignored
- Virtual environment ignored
- Jupyter cache ignored

See `.gitignore` for full policy.

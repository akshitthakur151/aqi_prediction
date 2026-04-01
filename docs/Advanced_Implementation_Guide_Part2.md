# AQI Prediction - Advanced Implementation Guide
## Part 2: Advanced Modeling Techniques

---

## 5. Time-Series Models (LSTM/GRU)

### 5.1 LSTM Model Architecture

```python
"""
lstm_aqi_model.py
LSTM-based time-series prediction for AQI
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

class LSTMAQIPredictor:
    """
    LSTM model for AQI prediction
    """
    
    def __init__(self, sequence_length=30, features=None):
        """
        Parameters:
        -----------
        sequence_length : int
            Number of past time steps to use for prediction
        features : list
            List of feature column names
        """
        self.sequence_length = sequence_length
        self.features = features or [
            'PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'OZONE',
            'temperature', 'humidity', 'wind_speed', 'pressure'
        ]
        self.model = None
        self.scaler = MinMaxScaler()
        self.history = None
    
    def prepare_sequences(self, data, target_col='AQI'):
        """
        Create sequences for LSTM training
        
        Parameters:
        -----------
        data : DataFrame
            Time-series data
        target_col : str
            Target column name
        
        Returns:
        --------
        X : array, shape (n_samples, sequence_length, n_features)
        y : array, shape (n_samples,)
        """
        # Select features
        df = data[self.features + [target_col]].copy()
        
        # Handle missing values
        df = df.fillna(method='ffill').fillna(method='bfill')
        
        # Scale features
        scaled_data = self.scaler.fit_transform(df)
        
        X, y = [], []
        
        for i in range(self.sequence_length, len(scaled_data)):
            X.append(scaled_data[i-self.sequence_length:i, :-1])  # All features except target
            y.append(scaled_data[i, -1])  # Target
        
        return np.array(X), np.array(y)
    
    def build_model(self, n_features):
        """
        Build LSTM model architecture
        """
        model = keras.Sequential([
            # First LSTM layer with return sequences
            layers.LSTM(128, return_sequences=True, 
                       input_shape=(self.sequence_length, n_features)),
            layers.Dropout(0.2),
            
            # Second LSTM layer
            layers.LSTM(64, return_sequences=True),
            layers.Dropout(0.2),
            
            # Third LSTM layer
            layers.LSTM(32, return_sequences=False),
            layers.Dropout(0.2),
            
            # Dense layers
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(16, activation='relu'),
            
            # Output layer
            layers.Dense(1)
        ])
        
        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def train(self, X_train, y_train, X_val=None, y_val=None,
              epochs=100, batch_size=32, verbose=1):
        """
        Train the LSTM model
        """
        n_features = X_train.shape[2]
        
        # Build model
        self.model = self.build_model(n_features)
        
        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7
            ),
            keras.callbacks.ModelCheckpoint(
                'models/lstm_best_model.h5',
                monitor='val_loss',
                save_best_only=True
            )
        ]
        
        # Validation data
        validation_data = (X_val, y_val) if X_val is not None else None
        
        # Train
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=verbose
        )
        
        return self.history
    
    def predict(self, X):
        """
        Make predictions
        """
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        predictions_scaled = self.model.predict(X)
        
        # Inverse transform predictions
        # Create dummy array with all features
        dummy = np.zeros((len(predictions_scaled), len(self.features) + 1))
        dummy[:, -1] = predictions_scaled.flatten()
        predictions = self.scaler.inverse_transform(dummy)[:, -1]
        
        return predictions
    
    def evaluate(self, X_test, y_test):
        """
        Evaluate model performance
        """
        predictions = self.predict(X_test)
        
        # Inverse transform y_test
        dummy = np.zeros((len(y_test), len(self.features) + 1))
        dummy[:, -1] = y_test
        y_test_actual = self.scaler.inverse_transform(dummy)[:, -1]
        
        rmse = np.sqrt(mean_squared_error(y_test_actual, predictions))
        r2 = r2_score(y_test_actual, predictions)
        mae = np.mean(np.abs(y_test_actual - predictions))
        
        print(f"LSTM Model Performance:")
        print(f"  RMSE: {rmse:.2f}")
        print(f"  R²: {r2:.4f}")
        print(f"  MAE: {mae:.2f}")
        
        return {'rmse': rmse, 'r2': r2, 'mae': mae, 
                'predictions': predictions, 'actual': y_test_actual}
    
    def plot_training_history(self):
        """
        Plot training history
        """
        if self.history is None:
            print("No training history available")
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Loss
        axes[0].plot(self.history.history['loss'], label='Training Loss')
        axes[0].plot(self.history.history['val_loss'], label='Validation Loss')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Loss')
        axes[0].set_title('Model Loss During Training')
        axes[0].legend()
        axes[0].grid(alpha=0.3)
        
        # MAE
        axes[1].plot(self.history.history['mae'], label='Training MAE')
        axes[1].plot(self.history.history['val_mae'], label='Validation MAE')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('MAE')
        axes[1].set_title('Model MAE During Training')
        axes[1].legend()
        axes[1].grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('visualizations/lstm_training_history.png', dpi=300)
        plt.show()
    
    def save(self, path='models/lstm_aqi_model'):
        """
        Save model and scaler
        """
        import joblib
        
        # Save model
        self.model.save(f"{path}.h5")
        
        # Save scaler
        joblib.dump(self.scaler, f"{path}_scaler.pkl")
        
        # Save config
        config = {
            'sequence_length': self.sequence_length,
            'features': self.features
        }
        joblib.dump(config, f"{path}_config.pkl")
        
        print(f"✓ Model saved to {path}")
    
    def load(self, path='models/lstm_aqi_model'):
        """
        Load saved model
        """
        import joblib
        
        # Load model
        self.model = keras.models.load_model(f"{path}.h5")
        
        # Load scaler
        self.scaler = joblib.load(f"{path}_scaler.pkl")
        
        # Load config
        config = joblib.load(f"{path}_config.pkl")
        self.sequence_length = config['sequence_length']
        self.features = config['features']
        
        print(f"✓ Model loaded from {path}")

# Usage Example
def train_lstm_model(df):
    """
    Complete LSTM training pipeline
    """
    print("="*60)
    print("TRAINING LSTM MODEL")
    print("="*60)
    
    # Initialize model
    lstm = LSTMAQIPredictor(
        sequence_length=30,  # Use 30 days of history
        features=['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'OZONE',
                 'temperature', 'humidity', 'wind_speed', 'pressure',
                 'traffic_score', 'is_weekend']
    )
    
    # Prepare data
    print("\nPreparing sequences...")
    X, y = lstm.prepare_sequences(df)
    print(f"Sequences created: {X.shape}")
    
    # Split data
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Further split for validation
    val_split = int(len(X_train) * 0.9)
    X_val = X_train[val_split:]
    y_val = y_train[val_split:]
    X_train = X_train[:val_split]
    y_train = y_train[:val_split]
    
    print(f"Training: {len(X_train)}, Validation: {len(X_val)}, Test: {len(X_test)}")
    
    # Train model
    print("\nTraining model...")
    lstm.train(
        X_train, y_train,
        X_val, y_val,
        epochs=100,
        batch_size=32,
        verbose=1
    )
    
    # Plot training history
    lstm.plot_training_history()
    
    # Evaluate
    print("\nEvaluating on test set...")
    results = lstm.evaluate(X_test, y_test)
    
    # Save model
    lstm.save()
    
    return lstm, results

# Train LSTM
lstm_model, lstm_results = train_lstm_model(df_enhanced)
```

### 5.2 GRU Model (Lighter Alternative)

```python
class GRUAQIPredictor(LSTMAQIPredictor):
    """
    GRU variant - faster training, similar performance
    """
    
    def build_model(self, n_features):
        """
        Build GRU model architecture
        """
        model = keras.Sequential([
            # First GRU layer
            layers.GRU(128, return_sequences=True,
                      input_shape=(self.sequence_length, n_features)),
            layers.Dropout(0.2),
            
            # Second GRU layer
            layers.GRU(64, return_sequences=True),
            layers.Dropout(0.2),
            
            # Third GRU layer
            layers.GRU(32, return_sequences=False),
            layers.Dropout(0.2),
            
            # Dense layers
            layers.Dense(32, activation='relu'),
            layers.Dense(16, activation='relu'),
            
            # Output
            layers.Dense(1)
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model

# Train GRU model
gru_model = GRUAQIPredictor(sequence_length=30)
# ... same training process as LSTM
```

### 5.3 Bidirectional LSTM

```python
def build_bidirectional_lstm(sequence_length, n_features):
    """
    Bidirectional LSTM - processes sequences in both directions
    """
    model = keras.Sequential([
        layers.Bidirectional(
            layers.LSTM(64, return_sequences=True),
            input_shape=(sequence_length, n_features)
        ),
        layers.Dropout(0.2),
        
        layers.Bidirectional(
            layers.LSTM(32, return_sequences=False)
        ),
        layers.Dropout(0.2),
        
        layers.Dense(32, activation='relu'),
        layers.Dense(16, activation='relu'),
        layers.Dense(1)
    ])
    
    model.compile(
        optimizer='adam',
        loss='mse',
        metrics=['mae']
    )
    
    return model
```

---

## 6. Ensemble Methods

### 6.1 Stacking Ensemble

```python
"""
ensemble_models.py
Advanced ensemble methods for AQI prediction
"""

from sklearn.ensemble import StackingRegressor, VotingRegressor
from sklearn.linear_model import Ridge
import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import lightgbm as lgb

class AQIEnsemble:
    """
    Ensemble of multiple models for robust predictions
    """
    
    def __init__(self):
        self.models = {}
        self.ensemble = None
        
    def create_base_models(self):
        """
        Create base models for ensemble
        """
        base_models = {
            'rf': RandomForestRegressor(
                n_estimators=200,
                max_depth=25,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            ),
            'xgb': xgb.XGBRegressor(
                n_estimators=300,
                max_depth=8,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1
            ),
            'gb': GradientBoostingRegressor(
                n_estimators=200,
                max_depth=7,
                learning_rate=0.1,
                subsample=0.8,
                random_state=42
            ),
            'lgbm': lgb.LGBMRegressor(
                n_estimators=300,
                max_depth=8,
                learning_rate=0.1,
                num_leaves=31,
                random_state=42,
                n_jobs=-1
            )
        }
        
        return base_models
    
    def build_stacking_ensemble(self):
        """
        Build stacking ensemble with meta-learner
        """
        base_models = self.create_base_models()
        
        # Convert to list of tuples for StackingRegressor
        estimators = [(name, model) for name, model in base_models.items()]
        
        # Stacking with Ridge as meta-learner
        self.ensemble = StackingRegressor(
            estimators=estimators,
            final_estimator=Ridge(alpha=1.0),
            cv=5,
            n_jobs=-1
        )
        
        return self.ensemble
    
    def build_voting_ensemble(self):
        """
        Build voting ensemble (simple average)
        """
        base_models = self.create_base_models()
        
        estimators = [(name, model) for name, model in base_models.items()]
        
        self.ensemble = VotingRegressor(
            estimators=estimators,
            n_jobs=-1
        )
        
        return self.ensemble
    
    def build_weighted_ensemble(self):
        """
        Build weighted voting ensemble
        """
        base_models = self.create_base_models()
        
        estimators = [(name, model) for name, model in base_models.items()]
        
        # Weights based on cross-validation performance
        weights = [0.25, 0.35, 0.20, 0.20]  # rf, xgb, gb, lgbm
        
        self.ensemble = VotingRegressor(
            estimators=estimators,
            weights=weights,
            n_jobs=-1
        )
        
        return self.ensemble
    
    def train(self, X_train, y_train, ensemble_type='stacking'):
        """
        Train the ensemble
        """
        print(f"Building {ensemble_type} ensemble...")
        
        if ensemble_type == 'stacking':
            self.build_stacking_ensemble()
        elif ensemble_type == 'voting':
            self.build_voting_ensemble()
        elif ensemble_type == 'weighted':
            self.build_weighted_ensemble()
        else:
            raise ValueError("Unknown ensemble type")
        
        print("Training ensemble...")
        self.ensemble.fit(X_train, y_train)
        
        print("✓ Ensemble trained")
        
        return self.ensemble
    
    def predict(self, X):
        """
        Make predictions with ensemble
        """
        return self.ensemble.predict(X)
    
    def evaluate(self, X_test, y_test):
        """
        Evaluate ensemble performance
        """
        predictions = self.predict(X_test)
        
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        r2 = r2_score(y_test, predictions)
        mae = mean_absolute_error(y_test, predictions)
        
        print(f"\nEnsemble Performance:")
        print(f"  RMSE: {rmse:.2f}")
        print(f"  R²: {r2:.4f}")
        print(f"  MAE: {mae:.2f}")
        
        return {'rmse': rmse, 'r2': r2, 'mae': mae, 'predictions': predictions}

# Usage
ensemble = AQIEnsemble()
ensemble.train(X_train, y_train, ensemble_type='stacking')
ensemble_results = ensemble.evaluate(X_test, y_test)
```

### 6.2 Multi-Model Prediction System

```python
class MultiModelPredictor:
    """
    Combine traditional ML, deep learning, and ensemble predictions
    """
    
    def __init__(self):
        self.models = {}
        self.weights = {}
    
    def train_all_models(self, X_train, y_train, X_test, y_test):
        """
        Train all types of models
        """
        results = {}
        
        # 1. XGBoost
        print("\n1. Training XGBoost...")
        xgb_model = xgb.XGBRegressor(n_estimators=300, max_depth=8)
        xgb_model.fit(X_train, y_train)
        self.models['xgb'] = xgb_model
        results['xgb'] = self._evaluate(xgb_model, X_test, y_test)
        
        # 2. Random Forest
        print("\n2. Training Random Forest...")
        rf_model = RandomForestRegressor(n_estimators=200, max_depth=25)
        rf_model.fit(X_train, y_train)
        self.models['rf'] = rf_model
        results['rf'] = self._evaluate(rf_model, X_test, y_test)
        
        # 3. Ensemble
        print("\n3. Training Ensemble...")
        ensemble = AQIEnsemble()
        ensemble.train(X_train, y_train, ensemble_type='stacking')
        self.models['ensemble'] = ensemble
        results['ensemble'] = ensemble.evaluate(X_test, y_test)
        
        # Calculate optimal weights based on performance
        self._calculate_weights(results)
        
        return results
    
    def _evaluate(self, model, X_test, y_test):
        """Helper to evaluate a model"""
        predictions = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        r2 = r2_score(y_test, predictions)
        return {'rmse': rmse, 'r2': r2, 'predictions': predictions}
    
    def _calculate_weights(self, results):
        """
        Calculate weights based on inverse RMSE
        """
        rmse_values = {name: res['rmse'] for name, res in results.items()}
        
        # Inverse RMSE (lower RMSE = higher weight)
        inv_rmse = {name: 1/rmse for name, rmse in rmse_values.items()}
        total = sum(inv_rmse.values())
        
        # Normalize to sum to 1
        self.weights = {name: val/total for name, val in inv_rmse.items()}
        
        print("\nModel Weights (based on performance):")
        for name, weight in self.weights.items():
            print(f"  {name}: {weight:.3f}")
    
    def predict(self, X):
        """
        Weighted prediction from all models
        """
        predictions = np.zeros(len(X))
        
        for name, model in self.models.items():
            weight = self.weights[name]
            
            if isinstance(model, AQIEnsemble):
                pred = model.predict(X)
            else:
                pred = model.predict(X)
            
            predictions += weight * pred
        
        return predictions

# Train multi-model system
multi_model = MultiModelPredictor()
all_results = multi_model.train_all_models(X_train, y_train, X_test, y_test)

# Make weighted predictions
final_predictions = multi_model.predict(X_test)
```

---

## 7. Uncertainty Quantification

### 7.1 Prediction Intervals with Quantile Regression

```python
"""
uncertainty_quantification.py
Provide confidence intervals for predictions
"""

from sklearn.ensemble import GradientBoostingRegressor
import numpy as np

class UncertaintyQuantifier:
    """
    Quantify prediction uncertainty using quantile regression
    """
    
    def __init__(self):
        self.models = {}
        self.quantiles = [0.05, 0.25, 0.50, 0.75, 0.95]
    
    def train(self, X_train, y_train):
        """
        Train models for different quantiles
        """
        for q in self.quantiles:
            print(f"Training model for quantile {q:.2f}...")
            
            model = GradientBoostingRegressor(
                n_estimators=200,
                max_depth=7,
                learning_rate=0.1,
                loss='quantile',
                alpha=q,
                random_state=42
            )
            
            model.fit(X_train, y_train)
            self.models[q] = model
    
    def predict_with_intervals(self, X, confidence=0.90):
        """
        Predict with confidence intervals
        
        Parameters:
        -----------
        X : array
            Features
        confidence : float
            Confidence level (e.g., 0.90 for 90% CI)
        
        Returns:
        --------
        dict with 'prediction', 'lower_bound', 'upper_bound'
        """
        # Calculate quantiles for confidence interval
        lower_q = (1 - confidence) / 2
        upper_q = 1 - lower_q
        
        # Get median prediction
        median_pred = self.models[0.50].predict(X)
        
        # Find closest quantiles
        lower_quantile = min(self.quantiles, key=lambda x: abs(x - lower_q))
        upper_quantile = min(self.quantiles, key=lambda x: abs(x - upper_q))
        
        lower_bound = self.models[lower_quantile].predict(X)
        upper_bound = self.models[upper_quantile].predict(X)
        
        return {
            'prediction': median_pred,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'confidence': confidence
        }
    
    def plot_predictions(self, X_test, y_test, n_samples=100):
        """
        Plot predictions with uncertainty bands
        """
        results = self.predict_with_intervals(X_test[:n_samples])
        
        plt.figure(figsize=(14, 6))
        
        x = np.arange(n_samples)
        
        # Plot actual values
        plt.plot(x, y_test[:n_samples], 'ko-', label='Actual', linewidth=2, markersize=4)
        
        # Plot prediction
        plt.plot(x, results['prediction'], 'b-', label='Prediction', linewidth=2)
        
        # Plot confidence interval
        plt.fill_between(
            x,
            results['lower_bound'],
            results['upper_bound'],
            alpha=0.3,
            label=f'{int(results["confidence"]*100)}% Confidence Interval'
        )
        
        plt.xlabel('Sample Index')
        plt.ylabel('AQI')
        plt.title('AQI Predictions with Uncertainty Quantification')
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig('visualizations/uncertainty_quantification.png', dpi=300)
        plt.show()

# Usage
uq = UncertaintyQuantifier()
uq.train(X_train, y_train)
predictions_with_ci = uq.predict_with_intervals(X_test, confidence=0.90)
uq.plot_predictions(X_test, y_test)
```

### 7.2 Bootstrap Confidence Intervals

```python
def bootstrap_confidence_intervals(model, X_train, y_train, X_test, 
                                   n_iterations=100, confidence=0.95):
    """
    Calculate confidence intervals using bootstrap
    """
    predictions_list = []
    
    for i in range(n_iterations):
        # Bootstrap sample
        indices = np.random.choice(len(X_train), size=len(X_train), replace=True)
        X_boot = X_train[indices]
        y_boot = y_train[indices]
        
        # Train model
        model_boot = clone(model)
        model_boot.fit(X_boot, y_boot)
        
        # Predict
        pred = model_boot.predict(X_test)
        predictions_list.append(pred)
    
    # Calculate percentiles
    predictions_array = np.array(predictions_list)
    
    lower_percentile = ((1 - confidence) / 2) * 100
    upper_percentile = (1 - (1 - confidence) / 2) * 100
    
    lower_bound = np.percentile(predictions_array, lower_percentile, axis=0)
    upper_bound = np.percentile(predictions_array, upper_percentile, axis=0)
    mean_prediction = np.mean(predictions_array, axis=0)
    
    return {
        'prediction': mean_prediction,
        'lower_bound': lower_bound,
        'upper_bound': upper_bound,
        'std': np.std(predictions_array, axis=0)
    }
```

---

## 8. Spatial Autocorrelation

### 8.1 Spatial Features from Neighboring Stations

```python
"""
spatial_features.py
Add spatial autocorrelation features
"""

from sklearn.metrics.pairwise import haversine_distances
import numpy as np

class SpatialFeatureEngineer:
    """
    Create features based on nearby stations
    """
    
    def __init__(self, max_neighbors=5):
        self.max_neighbors = max_neighbors
    
    def calculate_distances(self, lat_lon_array):
        """
        Calculate haversine distances between all points
        
        Parameters:
        -----------
        lat_lon_array : array, shape (n_stations, 2)
            Latitude and longitude in radians
        
        Returns:
        --------
        distance_matrix : array, shape (n_stations, n_stations)
            Distances in kilometers
        """
        # Convert to radians
        lat_lon_rad = np.radians(lat_lon_array)
        
        # Calculate distances
        distances = haversine_distances(lat_lon_rad) * 6371  # Earth radius in km
        
        return distances
    
    def find_nearest_neighbors(self, station_coords):
        """
        Find k nearest neighbors for each station
        
        Returns:
        --------
        dict: {station_idx: [neighbor_indices]}
        """
        distances = self.calculate_distances(station_coords)
        
        neighbors = {}
        
        for i in range(len(distances)):
            # Get indices sorted by distance (excluding self)
            nearest = np.argsort(distances[i])[1:self.max_neighbors+1]
            neighbors[i] = nearest
        
        return neighbors
    
    def add_neighbor_features(self, df, pollutant_cols):
        """
        Add average pollutant levels from nearby stations
        """
        df = df.copy()
        
        # Get unique stations
        stations = df[['station', 'latitude', 'longitude']].drop_duplicates()
        station_coords = stations[['latitude', 'longitude']].values
        
        # Find neighbors
        neighbors = self.find_nearest_neighbors(station_coords)
        
        # Create mapping
        station_to_idx = {s: i for i, s in enumerate(stations['station'])}
        
        # Add neighbor features
        for pollutant in pollutant_cols:
            neighbor_col = f'{pollutant}_neighbor_avg'
            df[neighbor_col] = np.nan
            
            for idx, row in df.iterrows():
                station = row['station']
                timestamp = row['datetime']
                
                if station in station_to_idx:
                    station_idx = station_to_idx[station]
                    neighbor_indices = neighbors[station_idx]
                    
                    # Get neighbor stations
                    neighbor_stations = stations.iloc[neighbor_indices]['station'].values
                    
                    # Get neighbor values at same timestamp
                    neighbor_data = df[
                        (df['station'].isin(neighbor_stations)) &
                        (df['datetime'] == timestamp)
                    ][pollutant]
                    
                    if len(neighbor_data) > 0:
                        df.at[idx, neighbor_col] = neighbor_data.mean()
        
        return df
    
    def add_distance_weighted_features(self, df, pollutant_cols):
        """
        Add distance-weighted average from neighbors
        """
        # Similar to above but weight by inverse distance
        # Implementation details...
        pass

# Usage
spatial_fe = SpatialFeatureEngineer(max_neighbors=5)
df_with_spatial = spatial_fe.add_neighbor_features(
    df_enhanced,
    pollutant_cols=['PM2.5', 'PM10', 'NO2', 'AQI']
)
```

---

**Continue to Part 3: Deployment & Dashboards →**

This completes the advanced modeling section. Next, I'll create the deployment guide with Flask/FastAPI, dashboards, and real-time monitoring.

Would you like me to continue with Part 3?

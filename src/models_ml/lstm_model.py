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
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import joblib


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
        available_features = [f for f in self.features if f in data.columns]
        df = data[available_features + [target_col] if target_col in data.columns else available_features].copy()
        
        # Handle missing values
        df = df.fillna(method='ffill').fillna(method='bfill')
        
        # Scale features
        scaled_data = self.scaler.fit_transform(df)
        
        X, y = [], []
        
        # Determine target index
        if target_col in data.columns:
            target_idx = len(available_features)
            for i in range(self.sequence_length, len(scaled_data)):
                X.append(scaled_data[i-self.sequence_length:i, :-1])  # All features except target
                y.append(scaled_data[i, -1])  # Target
        else:
            # If no target, just prepare sequences for prediction
            for i in range(self.sequence_length, len(scaled_data)):
                X.append(scaled_data[i-self.sequence_length:i, :])
        
        return np.array(X), np.array(y) if len(y) > 0 else None
    
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
        mae = mean_absolute_error(y_test_actual, predictions)
        
        print(f"\nLSTM Model Performance:")
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
        if 'val_loss' in self.history.history:
            axes[0].plot(self.history.history['val_loss'], label='Validation Loss')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Loss')
        axes[0].set_title('Model Loss During Training')
        axes[0].legend()
        axes[0].grid(alpha=0.3)
        
        # MAE
        axes[1].plot(self.history.history['mae'], label='Training MAE')
        if 'val_mae' in self.history.history:
            axes[1].plot(self.history.history['val_mae'], label='Validation MAE')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('MAE')
        axes[1].set_title('Model MAE During Training')
        axes[1].legend()
        axes[1].grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('visualizations/lstm_training_history.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("✓ Training history plot saved")
    
    def save(self, path='models/lstm_aqi_model'):
        """
        Save model and scaler
        """
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
        
        print(f"✓ LSTM Model saved to {path}")
    
    def load(self, path='models/lstm_aqi_model'):
        """
        Load saved model
        """
        # Load model
        self.model = keras.models.load_model(f"{path}.h5")
        
        # Load scaler
        self.scaler = joblib.load(f"{path}_scaler.pkl")
        
        # Load config
        config = joblib.load(f"{path}_config.pkl")
        self.sequence_length = config['sequence_length']
        self.features = config['features']
        
        print(f"✓ LSTM Model loaded from {path}")


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


# Usage example
if __name__ == "__main__":
    print("LSTM/GRU AQI Model Module Loaded")
    print("Ready to train time-series models")
    
    # Example usage:
    # lstm = LSTMAQIPredictor(sequence_length=30)
    # X, y = lstm.prepare_sequences(df_engineered)
    # X_train, X_test = X[:split], X[split:]
    # y_train, y_test = y[:split], y[split:]
    # lstm.train(X_train, y_train, X_test, y_test, epochs=100)
    # results = lstm.evaluate(X_test, y_test)
    # lstm.save()

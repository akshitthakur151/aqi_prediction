"""
ensemble_models.py
Advanced ensemble methods for AQI prediction
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import StackingRegressor, VotingRegressor, RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import xgboost as xgb
import joblib

try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False


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
        }
        
        if HAS_LIGHTGBM:
            base_models['lgbm'] = lgb.LGBMRegressor(
                n_estimators=300,
                max_depth=8,
                learning_rate=0.1,
                num_leaves=31,
                random_state=42,
                n_jobs=-1,
                verbose=-1
            )
        
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
        
        # Weights based on expected cross-validation performance
        n_models = len(estimators)
        if n_models == 4:
            weights = [0.25, 0.35, 0.20, 0.20]  # rf, xgb, gb, lgbm
        else:
            weights = [1.0 / n_models] * n_models
        
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
        if self.ensemble is None:
            raise ValueError("Ensemble not trained yet!")
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
    
    def save(self, path='models/ensemble_aqi_model.pkl'):
        """
        Save ensemble model
        """
        joblib.dump(self.ensemble, path)
        print(f"✓ Ensemble model saved to {path}")
    
    def load(self, path='models/ensemble_aqi_model.pkl'):
        """
        Load saved ensemble model
        """
        self.ensemble = joblib.load(path)
        print(f"✓ Ensemble model loaded from {path}")


class MultiModelPredictor:
    """
    Combine traditional ML, deep learning, and ensemble predictions
    """
    
    def __init__(self):
        self.models = {}
        self.weights = {}
        self.predictions = {}
    
    def add_model(self, name, model, weight=1.0):
        """
        Add a model to the multi-model system
        """
        self.models[name] = model
        self.weights[name] = weight
    
    def predict_all(self, X):
        """
        Get predictions from all models
        """
        predictions = {}
        
        for name, model in self.models.items():
            try:
                pred = model.predict(X)
                predictions[name] = pred
            except Exception as e:
                print(f"Error in model {name}: {e}")
        
        return predictions
    
    def combine_predictions(self, X, method='weighted_average'):
        """
        Combine predictions from multiple models
        """
        predictions = self.predict_all(X)
        
        if not predictions:
            raise ValueError("No predictions available")
        
        if method == 'weighted_average':
            # Normalize weights
            total_weight = sum(self.weights[name] for name in predictions.keys())
            weights = {name: self.weights[name] / total_weight for name in predictions.keys()}
            
            combined = np.zeros_like(list(predictions.values())[0])
            for name, pred in predictions.items():
                combined += pred * weights[name]
            
            return combined
        
        elif method == 'majority_vote':
            # For classification (if needed)
            combined = np.mean(list(predictions.values()), axis=0)
            return combined
        
        elif method == 'median':
            combined = np.median(list(predictions.values()), axis=0)
            return combined
        
        else:
            raise ValueError("Unknown combination method")
    
    def evaluate_all(self, X_test, y_test):
        """
        Evaluate all models
        """
        print("\nEvaluating all models:")
        print("=" * 60)
        
        results = {}
        
        for name, model in self.models.items():
            try:
                pred = model.predict(X_test)
                rmse = np.sqrt(mean_squared_error(y_test, pred))
                r2 = r2_score(y_test, pred)
                mae = mean_absolute_error(y_test, pred)
                
                results[name] = {'rmse': rmse, 'r2': r2, 'mae': mae}
                print(f"{name:15} | RMSE: {rmse:7.2f} | R²: {r2:.4f} | MAE: {mae:7.2f}")
            
            except Exception as e:
                print(f"{name:15} | Error: {e}")
        
        # Combined predictions
        combined_pred = self.combine_predictions(X_test, method='weighted_average')
        combined_rmse = np.sqrt(mean_squared_error(y_test, combined_pred))
        combined_r2 = r2_score(y_test, combined_pred)
        combined_mae = mean_absolute_error(y_test, combined_pred)
        
        results['combined'] = {'rmse': combined_rmse, 'r2': combined_r2, 'mae': combined_mae}
        print("=" * 60)
        print(f"{'COMBINED':15} | RMSE: {combined_rmse:7.2f} | R²: {combined_r2:.4f} | MAE: {combined_mae:7.2f}")
        
        return results


# Usage example
if __name__ == "__main__":
    print("Ensemble Models Module Loaded")
    print("Ready to train ensemble models")
    
    # Example usage:
    # ensemble = AQIEnsemble()
    # ensemble.train(X_train, y_train, ensemble_type='stacking')
    # results = ensemble.evaluate(X_test, y_test)
    # ensemble.save()

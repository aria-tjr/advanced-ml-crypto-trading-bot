"""
XGBoost Model for Price Prediction
Gradient boosting model for cryptocurrency price forecasting
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path
from loguru import logger


class XGBoostModel:
    """XGBoost model for price prediction"""
    
    def __init__(self, lookback_period: int = 100, prediction_horizon: int = 1):
        """
        Initialize XGBoost model
        
        Args:
            lookback_period: Number of historical periods to use
            prediction_horizon: Number of periods ahead to predict
        """
        self.lookback_period = lookback_period
        self.prediction_horizon = prediction_horizon
        self.model = None
        self.scaler = StandardScaler()
        self.feature_importance = None
        
        # XGBoost parameters
        self.params = {
            'objective': 'reg:squarederror',
            'max_depth': 8,
            'learning_rate': 0.01,
            'n_estimators': 1000,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'gamma': 0.1,
            'reg_alpha': 0.1,
            'reg_lambda': 1.0,
            'random_state': 42,
            'n_jobs': -1,
            'early_stopping_rounds': 50
        }
    
    def prepare_data(self, df: pd.DataFrame, target_col: str = 'close') -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for training
        
        Args:
            df: DataFrame with features
            target_col: Target column name
            
        Returns:
            Tuple of (X, y) arrays
        """
        # Create target (future price change)
        df['target'] = df[target_col].shift(-self.prediction_horizon) / df[target_col] - 1
        
        # Remove rows with NaN in target
        df = df.dropna(subset=['target'])
        
        # Separate features and target
        feature_cols = [col for col in df.columns if col not in ['target', 'timestamp']]
        X = df[feature_cols].values
        y = df['target'].values
        
        # Scale features
        X = self.scaler.fit_transform(X)
        
        return X, y
    
    def train(self, X: np.ndarray, y: np.ndarray, validation_split: float = 0.2) -> Dict:
        """
        Train XGBoost model
        
        Args:
            X: Feature array
            y: Target array
            validation_split: Validation data fraction
            
        Returns:
            Training metrics dictionary
        """
        # Split data
        split_idx = int(len(X) * (1 - validation_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Create model
        self.model = xgb.XGBRegressor(**self.params)
        
        # Train with early stopping
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )
        
        # Calculate metrics
        train_pred = self.model.predict(X_train)
        val_pred = self.model.predict(X_val)
        
        metrics = {
            'train_rmse': np.sqrt(np.mean((y_train - train_pred) ** 2)),
            'val_rmse': np.sqrt(np.mean((y_val - val_pred) ** 2)),
            'train_mae': np.mean(np.abs(y_train - train_pred)),
            'val_mae': np.mean(np.abs(y_val - val_pred)),
            'train_r2': self.model.score(X_train, y_train),
            'val_r2': self.model.score(X_val, y_val)
        }
        
        # Get feature importance
        self.feature_importance = self.model.feature_importances_
        
        logger.info(f"XGBoost training complete. Val RMSE: {metrics['val_rmse']:.6f}")
        
        return metrics
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Feature array
            
        Returns:
            Predictions array
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def predict_proba(self, X: np.ndarray, threshold: float = 0.001) -> np.ndarray:
        """
        Predict direction (up/down) probability
        
        Args:
            X: Feature array
            threshold: Minimum change to consider as signal
            
        Returns:
            Probability of upward movement
        """
        predictions = self.predict(X)
        
        # Convert to direction signal
        signals = np.where(predictions > threshold, 1, np.where(predictions < -threshold, -1, 0))
        
        return signals
    
    def cross_validate(self, X: np.ndarray, y: np.ndarray, n_splits: int = 5) -> Dict:
        """
        Perform time series cross-validation
        
        Args:
            X: Feature array
            y: Target array
            n_splits: Number of CV splits
            
        Returns:
            CV metrics dictionary
        """
        tscv = TimeSeriesSplit(n_splits=n_splits)
        
        rmse_scores = []
        mae_scores = []
        r2_scores = []
        
        for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            
            model = xgb.XGBRegressor(**self.params)
            model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
            
            val_pred = model.predict(X_val)
            
            rmse_scores.append(np.sqrt(np.mean((y_val - val_pred) ** 2)))
            mae_scores.append(np.mean(np.abs(y_val - val_pred)))
            r2_scores.append(model.score(X_val, y_val))
            
            logger.info(f"Fold {fold + 1}/{n_splits} - RMSE: {rmse_scores[-1]:.6f}")
        
        return {
            'mean_rmse': np.mean(rmse_scores),
            'std_rmse': np.std(rmse_scores),
            'mean_mae': np.mean(mae_scores),
            'std_mae': np.std(mae_scores),
            'mean_r2': np.mean(r2_scores),
            'std_r2': np.std(r2_scores)
        }
    
    def get_feature_importance(self, feature_names: list, top_n: int = 20) -> pd.DataFrame:
        """
        Get top feature importances
        
        Args:
            feature_names: List of feature names
            top_n: Number of top features to return
            
        Returns:
            DataFrame with feature importances
        """
        if self.feature_importance is None:
            raise ValueError("Model not trained yet")
        
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': self.feature_importance
        })
        
        return importance_df.sort_values('importance', ascending=False).head(top_n)
    
    def save(self, path: Path) -> None:
        """Save model to disk"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        path.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(self.model, path / 'xgboost_model.pkl')
        joblib.dump(self.scaler, path / 'scaler.pkl')
        
        logger.info(f"Model saved to {path}")
    
    def load(self, path: Path) -> None:
        """Load model from disk"""
        self.model = joblib.load(path / 'xgboost_model.pkl')
        self.scaler = joblib.load(path / 'scaler.pkl')
        
        logger.info(f"Model loaded from {path}")

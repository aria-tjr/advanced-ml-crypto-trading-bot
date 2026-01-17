"""
LSTM Model for Time Series Prediction
Long Short-Term Memory neural network for cryptocurrency forecasting
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path
from loguru import logger


class TimeSeriesDataset(Dataset):
    """PyTorch dataset for time series data"""
    
    def __init__(self, X: np.ndarray, y: np.ndarray):
        self.X = torch.FloatTensor(X)
        self.y = torch.FloatTensor(y)
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


class LSTMNetwork(nn.Module):
    """LSTM neural network architecture"""
    
    def __init__(self, input_size: int, hidden_size: int = 128, num_layers: int = 2, 
                 dropout: float = 0.2):
        super(LSTMNetwork, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )
        
        # Fully connected layers
        self.fc1 = nn.Linear(hidden_size, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 1)
        
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x):
        # LSTM forward pass
        lstm_out, _ = self.lstm(x)
        
        # Take the last output
        last_output = lstm_out[:, -1, :]
        
        # Fully connected layers
        out = self.relu(self.fc1(last_output))
        out = self.dropout(out)
        out = self.relu(self.fc2(out))
        out = self.dropout(out)
        out = self.fc3(out)
        
        return out


class LSTMModel:
    """LSTM model for time series prediction"""
    
    def __init__(self, lookback_period: int = 100, prediction_horizon: int = 1,
                 hidden_size: int = 128, num_layers: int = 2, learning_rate: float = 0.001):
        """
        Initialize LSTM model
        
        Args:
            lookback_period: Number of historical time steps
            prediction_horizon: Number of steps ahead to predict
            hidden_size: LSTM hidden layer size
            num_layers: Number of LSTM layers
            learning_rate: Learning rate for optimizer
        """
        self.lookback_period = lookback_period
        self.prediction_horizon = prediction_horizon
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.learning_rate = learning_rate
        
        self.model = None
        self.scaler = StandardScaler()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        logger.info(f"Using device: {self.device}")
    
    def prepare_sequences(self, data: np.ndarray, target: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare sequences for LSTM
        
        Args:
            data: Feature data
            target: Target data
            
        Returns:
            Tuple of (X_sequences, y_sequences)
        """
        X_sequences = []
        y_sequences = []
        
        for i in range(len(data) - self.lookback_period - self.prediction_horizon + 1):
            X_sequences.append(data[i:i + self.lookback_period])
            y_sequences.append(target[i + self.lookback_period + self.prediction_horizon - 1])
        
        return np.array(X_sequences), np.array(y_sequences)
    
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
        df = df.dropna(subset=['target'])
        
        # Separate features and target
        feature_cols = [col for col in df.columns if col not in ['target', 'timestamp']]
        X = df[feature_cols].values
        y = df['target'].values
        
        # Scale features
        X = self.scaler.fit_transform(X)
        
        # Create sequences
        X_seq, y_seq = self.prepare_sequences(X, y)
        
        return X_seq, y_seq
    
    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 100, 
              batch_size: int = 32, validation_split: float = 0.2) -> Dict:
        """
        Train LSTM model
        
        Args:
            X: Feature sequences
            y: Target values
            epochs: Number of training epochs
            batch_size: Batch size
            validation_split: Validation data fraction
            
        Returns:
            Training history dictionary
        """
        # Split data
        split_idx = int(len(X) * (1 - validation_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Create datasets
        train_dataset = TimeSeriesDataset(X_train, y_train)
        val_dataset = TimeSeriesDataset(X_val, y_val)
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        
        # Initialize model
        input_size = X.shape[2]
        self.model = LSTMNetwork(input_size, self.hidden_size, self.num_layers).to(self.device)
        
        # Loss and optimizer
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', 
                                                                 factor=0.5, patience=10)
        
        # Training loop
        history = {'train_loss': [], 'val_loss': []}
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(epochs):
            # Training
            self.model.train()
            train_losses = []
            
            for batch_X, batch_y in train_loader:
                batch_X = batch_X.to(self.device)
                batch_y = batch_y.to(self.device)
                
                optimizer.zero_grad()
                outputs = self.model(batch_X).squeeze()
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                
                train_losses.append(loss.item())
            
            # Validation
            self.model.eval()
            val_losses = []
            
            with torch.no_grad():
                for batch_X, batch_y in val_loader:
                    batch_X = batch_X.to(self.device)
                    batch_y = batch_y.to(self.device)
                    
                    outputs = self.model(batch_X).squeeze()
                    loss = criterion(outputs, batch_y)
                    val_losses.append(loss.item())
            
            train_loss = np.mean(train_losses)
            val_loss = np.mean(val_losses)
            
            history['train_loss'].append(train_loss)
            history['val_loss'].append(val_loss)
            
            scheduler.step(val_loss)
            
            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch {epoch + 1}/{epochs} - Train Loss: {train_loss:.6f}, Val Loss: {val_loss:.6f}")
            
            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= 20:
                    logger.info(f"Early stopping at epoch {epoch + 1}")
                    break
        
        return history
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Feature sequences
            
        Returns:
            Predictions array
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        self.model.eval()
        
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X).to(self.device)
            predictions = self.model(X_tensor).cpu().numpy().squeeze()
        
        return predictions
    
    def save(self, path: Path) -> None:
        """Save model to disk"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        path.mkdir(parents=True, exist_ok=True)
        
        torch.save(self.model.state_dict(), path / 'lstm_model.pth')
        joblib.dump(self.scaler, path / 'scaler.pkl')
        
        # Save model config
        config = {
            'lookback_period': self.lookback_period,
            'prediction_horizon': self.prediction_horizon,
            'hidden_size': self.hidden_size,
            'num_layers': self.num_layers
        }
        joblib.dump(config, path / 'lstm_config.pkl')
        
        logger.info(f"Model saved to {path}")
    
    def load(self, path: Path, input_size: int) -> None:
        """Load model from disk"""
        config = joblib.load(path / 'lstm_config.pkl')
        
        self.model = LSTMNetwork(input_size, config['hidden_size'], 
                                config['num_layers']).to(self.device)
        self.model.load_state_dict(torch.load(path / 'lstm_model.pth'))
        self.scaler = joblib.load(path / 'scaler.pkl')
        
        logger.info(f"Model loaded from {path}")

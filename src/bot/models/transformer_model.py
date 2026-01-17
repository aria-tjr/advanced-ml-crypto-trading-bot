"""
Transformer Model for Market Analysis
Attention-based transformer for cryptocurrency price prediction
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
import math


class PositionalEncoding(nn.Module):
    """Positional encoding for transformer"""
    
    def __init__(self, d_model: int, max_len: int = 5000):
        super(PositionalEncoding, self).__init__()
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * 
                            (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        return x + self.pe[:, :x.size(1)]


class TransformerNetwork(nn.Module):
    """Transformer architecture for time series"""
    
    def __init__(self, input_size: int, d_model: int = 128, nhead: int = 8,
                 num_encoder_layers: int = 3, dim_feedforward: int = 512,
                 dropout: float = 0.1):
        super(TransformerNetwork, self).__init__()
        
        self.d_model = d_model
        
        # Input projection
        self.input_projection = nn.Linear(input_size, d_model)
        
        # Positional encoding
        self.pos_encoder = PositionalEncoding(d_model)
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer,
            num_layers=num_encoder_layers
        )
        
        # Output layers
        self.fc1 = nn.Linear(d_model, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 1)
        
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x):
        # Project input to d_model dimensions
        x = self.input_projection(x)
        
        # Add positional encoding
        x = self.pos_encoder(x)
        
        # Transformer encoding
        x = self.transformer_encoder(x)
        
        # Take the last output
        x = x[:, -1, :]
        
        # Output layers
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        
        return x


class TimeSeriesDataset(Dataset):
    """PyTorch dataset for time series"""
    
    def __init__(self, X: np.ndarray, y: np.ndarray):
        self.X = torch.FloatTensor(X)
        self.y = torch.FloatTensor(y)
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


class TransformerModel:
    """Transformer model for price prediction"""
    
    def __init__(self, lookback_period: int = 100, prediction_horizon: int = 1,
                 d_model: int = 128, nhead: int = 8, num_encoder_layers: int = 3,
                 learning_rate: float = 0.0001):
        """
        Initialize Transformer model
        
        Args:
            lookback_period: Number of historical time steps
            prediction_horizon: Number of steps ahead to predict
            d_model: Dimension of model
            nhead: Number of attention heads
            num_encoder_layers: Number of encoder layers
            learning_rate: Learning rate
        """
        self.lookback_period = lookback_period
        self.prediction_horizon = prediction_horizon
        self.d_model = d_model
        self.nhead = nhead
        self.num_encoder_layers = num_encoder_layers
        self.learning_rate = learning_rate
        
        self.model = None
        self.scaler = StandardScaler()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        logger.info(f"Using device: {self.device}")
    
    def prepare_sequences(self, data: np.ndarray, target: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare sequences for Transformer"""
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
        # Create target
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
        Train Transformer model
        
        Args:
            X: Feature sequences
            y: Target values
            epochs: Number of training epochs
            batch_size: Batch size
            validation_split: Validation data fraction
            
        Returns:
            Training history
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
        self.model = TransformerNetwork(
            input_size, self.d_model, self.nhead, self.num_encoder_layers
        ).to(self.device)
        
        # Loss and optimizer
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.5, patience=10
        )
        
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
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                
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
        """Make predictions"""
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
        
        torch.save(self.model.state_dict(), path / 'transformer_model.pth')
        joblib.dump(self.scaler, path / 'scaler.pkl')
        
        config = {
            'lookback_period': self.lookback_period,
            'prediction_horizon': self.prediction_horizon,
            'd_model': self.d_model,
            'nhead': self.nhead,
            'num_encoder_layers': self.num_encoder_layers
        }
        joblib.dump(config, path / 'transformer_config.pkl')
        
        logger.info(f"Model saved to {path}")
    
    def load(self, path: Path, input_size: int) -> None:
        """Load model from disk"""
        config = joblib.load(path / 'transformer_config.pkl')
        
        self.model = TransformerNetwork(
            input_size, config['d_model'], config['nhead'], config['num_encoder_layers']
        ).to(self.device)
        self.model.load_state_dict(torch.load(path / 'transformer_model.pth'))
        self.scaler = joblib.load(path / 'scaler.pkl')
        
        logger.info(f"Model loaded from {path}")

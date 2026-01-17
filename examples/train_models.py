"""
Example: Train ML Models
Demonstrates how to train XGBoost, LSTM, and Transformer models
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from bot.config import load_config
from bot.exchanges.binance import BinanceExchange
from bot.data.pipeline import DataPipeline
from bot.models.xgboost_model import XGBoostModel
from bot.models.lstm_model import LSTMModel
from bot.models.transformer_model import TransformerModel
from loguru import logger


async def train_models():
    """Train all ML models"""
    
    # Load configuration
    config = load_config('config/config.yaml')
    
    # Initialize exchange
    exchange = BinanceExchange(
        api_key=None,  # Public data doesn't need API key
        api_secret=None,
        testnet=True
    )
    await exchange.connect()
    
    # Initialize data pipeline
    pipeline = DataPipeline(
        exchange=exchange,
        symbols=['BTCUSDT'],
        timeframe='1h',
        lookback_days=365
    )
    
    # Fetch and prepare data
    logger.info("Fetching historical data...")
    df = await pipeline.prepare_training_data('BTCUSDT')
    
    if df.empty:
        logger.error("No data available")
        await exchange.disconnect()
        return
    
    logger.info(f"Prepared {len(df)} samples with {len(df.columns)} features")
    
    # Train XGBoost
    logger.info("\n=== Training XGBoost ===")
    xgb_model = XGBoostModel(lookback_period=100, prediction_horizon=1)
    X, y = xgb_model.prepare_data(df)
    xgb_metrics = xgb_model.train(X, y)
    logger.info(f"XGBoost Metrics: {xgb_metrics}")
    xgb_model.save(Path('models/saved/BTCUSDT/xgboost'))
    
    # Train LSTM
    logger.info("\n=== Training LSTM ===")
    lstm_model = LSTMModel(lookback_period=100, prediction_horizon=1)
    X_seq, y_seq = lstm_model.prepare_data(df)
    lstm_history = lstm_model.train(X_seq, y_seq, epochs=50, batch_size=32)
    logger.info(f"LSTM Final Loss: {lstm_history['val_loss'][-1]:.6f}")
    lstm_model.save(Path('models/saved/BTCUSDT/lstm'))
    
    # Train Transformer
    logger.info("\n=== Training Transformer ===")
    transformer_model = TransformerModel(lookback_period=100, prediction_horizon=1)
    X_seq, y_seq = transformer_model.prepare_data(df)
    transformer_history = transformer_model.train(X_seq, y_seq, epochs=50, batch_size=32)
    logger.info(f"Transformer Final Loss: {transformer_history['val_loss'][-1]:.6f}")
    transformer_model.save(Path('models/saved/BTCUSDT/transformer'))
    
    logger.info("\n=== Training Complete ===")
    
    await exchange.disconnect()


if __name__ == '__main__':
    asyncio.run(train_models())

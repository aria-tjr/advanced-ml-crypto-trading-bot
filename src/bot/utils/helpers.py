# Utility Functions
Common utility functions for the trading bot

from typing import Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path


def format_price(price: float, decimals: int = 2) -> str:
    """Format price with appropriate decimals"""
    return f"${price:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format percentage"""
    return f"{value * 100:.{decimals}f}%"


def calculate_returns(prices: pd.Series) -> pd.Series:
    """Calculate returns from prices"""
    return prices.pct_change()


def calculate_cumulative_returns(returns: pd.Series) -> pd.Series:
    """Calculate cumulative returns"""
    return (1 + returns).cumprod() - 1


def calculate_drawdown(equity: pd.Series) -> pd.Series:
    """Calculate drawdown series"""
    running_max = equity.expanding().max()
    drawdown = (equity - running_max) / running_max
    return drawdown


def timestamp_to_datetime(timestamp: int) -> datetime:
    """Convert millisecond timestamp to datetime"""
    return datetime.fromtimestamp(timestamp / 1000)


def datetime_to_timestamp(dt: datetime) -> int:
    """Convert datetime to millisecond timestamp"""
    return int(dt.timestamp() * 1000)


def round_to_tick_size(price: float, tick_size: float) -> float:
    """Round price to exchange tick size"""
    return round(price / tick_size) * tick_size


def round_to_lot_size(quantity: float, lot_size: float) -> float:
    """Round quantity to exchange lot size"""
    return round(quantity / lot_size) * lot_size


def calculate_position_value(quantity: float, price: float) -> float:
    """Calculate position value"""
    return quantity * price


def calculate_leverage_required(position_value: float, collateral: float) -> float:
    """Calculate leverage required"""
    return position_value / collateral


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide, return default if denominator is zero"""
    if denominator == 0:
        return default
    return numerator / denominator


def save_json(data: Dict[Any, Any], filepath: Path) -> None:
    """Save data to JSON file"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def load_json(filepath: Path) -> Dict[Any, Any]:
    """Load data from JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def exponential_moving_average(data: np.ndarray, period: int) -> np.ndarray:
    """Calculate EMA"""
    alpha = 2 / (period + 1)
    ema = np.zeros_like(data)
    ema[0] = data[0]
    
    for i in range(1, len(data)):
        ema[i] = alpha * data[i] + (1 - alpha) * ema[i - 1]
    
    return ema


def is_market_open(exchange: str = 'binance') -> bool:
    """Check if market is open (crypto is 24/7)"""
    # Crypto markets are always open
    return True


def get_timeframe_minutes(timeframe: str) -> int:
    """Convert timeframe string to minutes"""
    timeframes = {
        '1m': 1,
        '5m': 5,
        '15m': 15,
        '30m': 30,
        '1h': 60,
        '4h': 240,
        '1d': 1440,
        '1w': 10080
    }
    return timeframes.get(timeframe, 60)


def get_next_candle_time(current_time: datetime, timeframe: str) -> datetime:
    """Get next candle close time"""
    minutes = get_timeframe_minutes(timeframe)
    next_time = current_time + timedelta(minutes=minutes)
    return next_time


def validate_config(config: Dict[Any, Any]) -> bool:
    """Validate configuration"""
    required_keys = ['exchange', 'trading', 'risk', 'ml']
    return all(key in config for key in required_keys)

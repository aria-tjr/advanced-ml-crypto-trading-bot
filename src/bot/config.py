"""
Configuration Management System
Handles all configuration loading and validation
"""

from typing import Dict, Any, Optional
import yaml
import os
from pathlib import Path
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ExchangeConfig(BaseModel):
    """Exchange API configuration"""
    name: str
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    testnet: bool = True
    rate_limit: int = 1200
    

class TradingConfig(BaseModel):
    """Trading parameters configuration"""
    symbols: list[str] = Field(default_factory=lambda: ["BTCUSDT", "ETHUSDT"])
    timeframe: str = "1h"
    max_positions: int = 5
    leverage: int = 10
    order_type: str = "LIMIT"
    

class RiskConfig(BaseModel):
    """Risk management configuration"""
    max_position_size: float = 0.1  # 10% of portfolio per position
    stop_loss_pct: float = 0.02  # 2%
    take_profit_pct: float = 0.04  # 4%
    max_daily_loss: float = 0.05  # 5%
    risk_per_trade: float = 0.01  # 1%
    use_kelly_criterion: bool = True
    

class MLConfig(BaseModel):
    """ML models configuration"""
    model_type: str = "ensemble"  # ensemble, xgboost, lstm, transformer
    retrain_interval: int = 24  # hours
    lookback_period: int = 100
    prediction_horizon: int = 1
    feature_count: int = 200
    

class BacktestConfig(BaseModel):
    """Backtesting configuration"""
    start_date: str = "2023-01-01"
    end_date: str = "2023-12-31"
    initial_capital: float = 10000.0
    commission: float = 0.0006  # 0.06%
    slippage: float = 0.0001  # 0.01%
    

class Config(BaseSettings):
    """Main configuration class"""
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Exchange
    exchange: ExchangeConfig = Field(default_factory=lambda: ExchangeConfig(name="binance"))
    
    # Trading
    trading: TradingConfig = Field(default_factory=TradingConfig)
    
    # Risk Management
    risk: RiskConfig = Field(default_factory=RiskConfig)
    
    # ML Models
    ml: MLConfig = Field(default_factory=MLConfig)
    
    # Backtesting
    backtest: BacktestConfig = Field(default_factory=BacktestConfig)
    
    # Paths
    data_dir: Path = Field(default=Path("data"))
    models_dir: Path = Field(default=Path("models"))
    logs_dir: Path = Field(default=Path("logs"))
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
    @classmethod
    def from_yaml(cls, config_path: str) -> "Config":
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        return cls(**config_dict)
    
    def to_yaml(self, output_path: str) -> None:
        """Save configuration to YAML file"""
        with open(output_path, 'w') as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from file or environment
    
    Args:
        config_path: Path to configuration YAML file
        
    Returns:
        Config object
    """
    if config_path and os.path.exists(config_path):
        return Config.from_yaml(config_path)
    
    # Try default locations
    default_paths = [
        "config/config.yaml",
        "config/config.yml",
        "../config/config.yaml",
    ]
    
    for path in default_paths:
        if os.path.exists(path):
            return Config.from_yaml(path)
    
    # Return default configuration
    return Config()

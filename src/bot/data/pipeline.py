"""
Data Pipeline
Real-time data fetching, preprocessing, and feature engineering
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
from loguru import logger

from bot.exchanges.base import BaseExchange
from bot.indicators.technical import IndicatorEngine


class DataPipeline:
    """Real-time data pipeline for crypto trading"""
    
    def __init__(self, exchange: BaseExchange, symbols: List[str], 
                 timeframe: str = '1h', lookback_days: int = 365):
        """
        Initialize data pipeline
        
        Args:
            exchange: Exchange client
            symbols: List of trading symbols
            timeframe: Candlestick timeframe
            lookback_days: Days of historical data to fetch
        """
        self.exchange = exchange
        self.symbols = symbols
        self.timeframe = timeframe
        self.lookback_days = lookback_days
        
        self.indicator_engine = IndicatorEngine()
        self.data_cache = {}
    
    async def fetch_historical_data(self, symbol: str, 
                                    start_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Fetch historical OHLCV data
        
        Args:
            symbol: Trading symbol
            start_date: Start date (default: lookback_days ago)
            
        Returns:
            DataFrame with OHLCV data
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=self.lookback_days)
        
        logger.info(f"Fetching historical data for {symbol}")
        
        try:
            df = await self.exchange.get_historical_data(
                symbol=symbol,
                timeframe=self.timeframe,
                start_time=start_date,
                limit=1000
            )
            
            if df.empty:
                logger.warning(f"No data received for {symbol}")
                return pd.DataFrame()
            
            logger.info(f"Fetched {len(df)} candles for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    async def fetch_all_symbols(self) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for all symbols
        
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        tasks = [self.fetch_historical_data(symbol) for symbol in self.symbols]
        results = await asyncio.gather(*tasks)
        
        data_dict = {}
        for symbol, df in zip(self.symbols, results):
            if not df.empty:
                data_dict[symbol] = df
                self.data_cache[symbol] = df
        
        return data_dict
    
    async def update_realtime_data(self, symbol: str) -> pd.DataFrame:
        """
        Update data with latest candle
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Updated DataFrame
        """
        try:
            # Fetch latest candle
            latest = await self.exchange.get_historical_data(
                symbol=symbol,
                timeframe=self.timeframe,
                limit=1
            )
            
            if symbol in self.data_cache and not latest.empty:
                # Append to cache
                self.data_cache[symbol] = pd.concat([
                    self.data_cache[symbol],
                    latest
                ]).drop_duplicates().tail(1000)  # Keep last 1000 candles
                
                return self.data_cache[symbol]
            
            return latest
            
        except Exception as e:
            logger.error(f"Error updating data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators and features
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with features
        """
        if df.empty:
            return df
        
        logger.debug(f"Calculating features for {len(df)} rows")
        
        try:
            # Calculate all indicators
            df_with_features = self.indicator_engine.calculate_all(df)
            
            # Clean features for ML
            df_with_features = self.indicator_engine.get_feature_importance_ready(df_with_features)
            
            logger.debug(f"Calculated {len(df_with_features.columns)} features")
            
            return df_with_features
            
        except Exception as e:
            logger.error(f"Error calculating features: {e}")
            return df
    
    async def prepare_training_data(self, symbol: str) -> pd.DataFrame:
        """
        Prepare data for model training
        
        Args:
            symbol: Trading symbol
            
        Returns:
            DataFrame ready for training
        """
        # Fetch data
        df = await self.fetch_historical_data(symbol)
        
        if df.empty:
            return pd.DataFrame()
        
        # Calculate features
        df = self.calculate_features(df)
        
        return df
    
    async def get_latest_features(self, symbol: str) -> pd.DataFrame:
        """
        Get latest features for prediction
        
        Args:
            symbol: Trading symbol
            
        Returns:
            DataFrame with latest features
        """
        # Update data
        df = await self.update_realtime_data(symbol)
        
        if df.empty:
            return pd.DataFrame()
        
        # Calculate features
        df = self.calculate_features(df)
        
        return df.tail(1)
    
    def split_train_test(self, df: pd.DataFrame, 
                        test_size: float = 0.2) -> tuple:
        """
        Split data into train and test sets
        
        Args:
            df: DataFrame with features
            test_size: Fraction of data for testing
            
        Returns:
            Tuple of (train_df, test_df)
        """
        split_idx = int(len(df) * (1 - test_size))
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]
        
        return train_df, test_df
    
    def save_data(self, df: pd.DataFrame, symbol: str, 
                 path: str = 'data/processed') -> None:
        """
        Save processed data to disk
        
        Args:
            df: DataFrame to save
            symbol: Trading symbol
            path: Save path
        """
        import os
        os.makedirs(path, exist_ok=True)
        
        filename = f"{path}/{symbol}_{self.timeframe}_{datetime.now().strftime('%Y%m%d')}.parquet"
        df.to_parquet(filename)
        
        logger.info(f"Saved data to {filename}")
    
    def load_data(self, symbol: str, path: str = 'data/processed') -> pd.DataFrame:
        """
        Load processed data from disk
        
        Args:
            symbol: Trading symbol
            path: Load path
            
        Returns:
            DataFrame with data
        """
        import glob
        
        pattern = f"{path}/{symbol}_{self.timeframe}_*.parquet"
        files = glob.glob(pattern)
        
        if not files:
            logger.warning(f"No saved data found for {symbol}")
            return pd.DataFrame()
        
        # Load most recent file
        latest_file = sorted(files)[-1]
        df = pd.read_parquet(latest_file)
        
        logger.info(f"Loaded data from {latest_file}")
        return df
    
    async def get_market_data_summary(self, symbol: str) -> Dict:
        """
        Get market data summary
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dictionary with market summary
        """
        try:
            ticker = await self.exchange.get_ticker(symbol)
            orderbook = await self.exchange.get_orderbook(symbol, limit=10)
            
            # Calculate order book imbalance
            bid_volume = sum([bid[1] for bid in orderbook['bids']])
            ask_volume = sum([ask[1] for ask in orderbook['asks']])
            imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume)
            
            return {
                'symbol': symbol,
                'last_price': ticker.get('last_price', 0),
                'bid': ticker.get('bid', 0),
                'ask': ticker.get('ask', 0),
                'volume': ticker.get('volume', 0),
                'change': ticker.get('change', 0),
                'orderbook_imbalance': imbalance,
                'spread': ticker.get('ask', 0) - ticker.get('bid', 0),
                'spread_pct': (ticker.get('ask', 0) - ticker.get('bid', 0)) / ticker.get('last_price', 1)
            }
            
        except Exception as e:
            logger.error(f"Error getting market summary: {e}")
            return {}

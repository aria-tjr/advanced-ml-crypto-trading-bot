"""
Market Regime Detection
Identifies different market conditions (trending, ranging, volatile, etc.)
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from sklearn.cluster import KMeans
from scipy import stats
from loguru import logger


class MarketRegimeDetector:
    """Detect and classify market regimes"""
    
    def __init__(self, n_regimes: int = 4):
        """
        Initialize regime detector
        
        Args:
            n_regimes: Number of market regimes to detect
        """
        self.n_regimes = n_regimes
        self.kmeans = KMeans(n_clusters=n_regimes, random_state=42)
        self.regime_labels = {
            0: 'low_volatility_bullish',
            1: 'high_volatility_bullish',
            2: 'low_volatility_bearish',
            3: 'high_volatility_bearish'
        }
    
    def calculate_regime_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate features for regime detection
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with regime features
        """
        close = df['close']
        high = df['high']
        low = df['low']
        volume = df['volume']
        
        # Returns
        df['returns'] = close.pct_change()
        df['log_returns'] = np.log(close / close.shift(1))
        
        # Volatility measures
        df['volatility_20'] = df['returns'].rolling(20).std()
        df['volatility_50'] = df['returns'].rolling(50).std()
        df['parkinson_vol'] = np.sqrt((np.log(high / low) ** 2) / (4 * np.log(2)))
        
        # Trend measures
        df['sma_20'] = close.rolling(20).mean()
        df['sma_50'] = close.rolling(50).mean()
        df['trend_strength'] = (close - df['sma_50']) / df['sma_50']
        df['price_momentum'] = close / close.shift(20) - 1
        
        # Volume measures
        df['volume_ratio'] = volume / volume.rolling(20).mean()
        df['volume_volatility'] = volume.rolling(20).std() / volume.rolling(20).mean()
        
        # Range measures
        df['true_range'] = np.maximum(high - low, 
                                     np.maximum(abs(high - close.shift(1)),
                                              abs(low - close.shift(1))))
        df['atr'] = df['true_range'].rolling(14).mean()
        df['atr_ratio'] = df['atr'] / close
        
        # Skewness and Kurtosis
        df['skewness'] = df['returns'].rolling(20).apply(lambda x: stats.skew(x))
        df['kurtosis'] = df['returns'].rolling(20).apply(lambda x: stats.kurtosis(x))
        
        return df
    
    def detect_regimes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect market regimes using clustering
        
        Args:
            df: DataFrame with regime features
            
        Returns:
            DataFrame with regime labels
        """
        # Features for clustering
        features = [
            'volatility_20', 'trend_strength', 'price_momentum',
            'volume_ratio', 'atr_ratio', 'skewness'
        ]
        
        # Remove NaN
        df_clean = df[features].dropna()
        
        if len(df_clean) < self.n_regimes:
            logger.warning("Not enough data for regime detection")
            df['regime'] = 0
            return df
        
        # Normalize features
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(df_clean)
        
        # Cluster
        regimes = self.kmeans.fit_predict(features_scaled)
        
        # Assign regimes back to dataframe
        df.loc[df_clean.index, 'regime'] = regimes
        df['regime'] = df['regime'].fillna(method='ffill').fillna(0)
        
        # Add regime labels
        df['regime_name'] = df['regime'].map(self.regime_labels)
        
        return df
    
    def classify_regime_simple(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Simple rule-based regime classification
        
        Args:
            df: DataFrame with features
            
        Returns:
            DataFrame with regime classification
        """
        # Calculate features if not present
        if 'volatility_20' not in df.columns:
            df = self.calculate_regime_features(df)
        
        # Define thresholds
        vol_threshold = df['volatility_20'].median()
        trend_threshold = 0
        
        # Classify regimes
        conditions = [
            (df['volatility_20'] < vol_threshold) & (df['trend_strength'] > trend_threshold),
            (df['volatility_20'] >= vol_threshold) & (df['trend_strength'] > trend_threshold),
            (df['volatility_20'] < vol_threshold) & (df['trend_strength'] <= trend_threshold),
            (df['volatility_20'] >= vol_threshold) & (df['trend_strength'] <= trend_threshold)
        ]
        
        choices = [0, 1, 2, 3]
        df['regime'] = np.select(conditions, choices, default=0)
        df['regime_name'] = df['regime'].map(self.regime_labels)
        
        return df
    
    def get_regime_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Get statistics for each regime
        
        Args:
            df: DataFrame with regimes
            
        Returns:
            Dictionary with regime statistics
        """
        stats_dict = {}
        
        for regime in df['regime'].unique():
            regime_data = df[df['regime'] == regime]
            
            stats_dict[int(regime)] = {
                'name': self.regime_labels.get(int(regime), 'unknown'),
                'count': len(regime_data),
                'avg_return': regime_data['returns'].mean(),
                'avg_volatility': regime_data['volatility_20'].mean(),
                'avg_volume': regime_data['volume'].mean(),
                'max_drawdown': self._calculate_max_drawdown(regime_data['close']),
                'sharpe_ratio': self._calculate_sharpe_ratio(regime_data['returns'])
            }
        
        return stats_dict
    
    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """Calculate maximum drawdown"""
        cumulative = (1 + prices.pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """Calculate Sharpe ratio"""
        excess_returns = returns - risk_free_rate
        if excess_returns.std() == 0:
            return 0
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()
    
    def get_current_regime(self, df: pd.DataFrame) -> Tuple[int, str]:
        """
        Get the current market regime
        
        Args:
            df: DataFrame with regimes
            
        Returns:
            Tuple of (regime_id, regime_name)
        """
        if 'regime' not in df.columns:
            df = self.detect_regimes(df)
        
        current_regime = int(df['regime'].iloc[-1])
        regime_name = self.regime_labels.get(current_regime, 'unknown')
        
        return current_regime, regime_name
    
    def detect_regime_change(self, df: pd.DataFrame, lookback: int = 10) -> bool:
        """
        Detect if regime has changed recently
        
        Args:
            df: DataFrame with regimes
            lookback: Number of periods to look back
            
        Returns:
            True if regime changed, False otherwise
        """
        if 'regime' not in df.columns or len(df) < lookback:
            return False
        
        recent_regimes = df['regime'].tail(lookback)
        return len(recent_regimes.unique()) > 1

"""
Technical Indicators Module
Comprehensive technical analysis indicators (200+)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import talib
import pandas_ta as ta
from loguru import logger


class IndicatorEngine:
    """Calculate 200+ technical indicators"""
    
    def __init__(self):
        self.indicator_groups = {
            'trend': self._calculate_trend_indicators,
            'momentum': self._calculate_momentum_indicators,
            'volatility': self._calculate_volatility_indicators,
            'volume': self._calculate_volume_indicators,
            'support_resistance': self._calculate_support_resistance,
            'pattern': self._calculate_pattern_indicators,
            'statistical': self._calculate_statistical_indicators,
            'custom': self._calculate_custom_indicators
        }
    
    def calculate_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all indicators
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with all indicators
        """
        result = df.copy()
        
        for group_name, calc_func in self.indicator_groups.items():
            try:
                result = calc_func(result)
                logger.debug(f"Calculated {group_name} indicators")
            except Exception as e:
                logger.error(f"Error calculating {group_name} indicators: {e}")
        
        return result
    
    def _calculate_trend_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate trend indicators (50+)"""
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        
        # Moving Averages
        for period in [5, 10, 20, 30, 50, 100, 200]:
            df[f'sma_{period}'] = talib.SMA(close, timeperiod=period)
            df[f'ema_{period}'] = talib.EMA(close, timeperiod=period)
            df[f'wma_{period}'] = talib.WMA(close, timeperiod=period)
            df[f'dema_{period}'] = talib.DEMA(close, timeperiod=period)
            df[f'tema_{period}'] = talib.TEMA(close, timeperiod=period)
        
        # MACD variations
        for fast, slow, signal in [(12, 26, 9), (5, 35, 5), (19, 39, 9)]:
            macd, signal_line, hist = talib.MACD(close, fastperiod=fast, 
                                                  slowperiod=slow, signalperiod=signal)
            df[f'macd_{fast}_{slow}'] = macd
            df[f'macd_signal_{fast}_{slow}'] = signal_line
            df[f'macd_hist_{fast}_{slow}'] = hist
        
        # ADX (Average Directional Index)
        for period in [14, 20, 30]:
            df[f'adx_{period}'] = talib.ADX(high, low, close, timeperiod=period)
            df[f'plus_di_{period}'] = talib.PLUS_DI(high, low, close, timeperiod=period)
            df[f'minus_di_{period}'] = talib.MINUS_DI(high, low, close, timeperiod=period)
        
        # Parabolic SAR
        df['sar'] = talib.SAR(high, low)
        
        # Supertrend
        df.ta.supertrend(length=10, multiplier=3, append=True)
        
        # Aroon
        df['aroon_up'], df['aroon_down'] = talib.AROON(high, low, timeperiod=14)
        df['aroon_osc'] = talib.AROONOSC(high, low, timeperiod=14)
        
        # HT_TRENDLINE
        df['ht_trendline'] = talib.HT_TRENDLINE(close)
        
        # Linear Regression
        for period in [14, 20, 50]:
            df[f'linearreg_{period}'] = talib.LINEARREG(close, timeperiod=period)
            df[f'linearreg_slope_{period}'] = talib.LINEARREG_SLOPE(close, timeperiod=period)
            df[f'linearreg_angle_{period}'] = talib.LINEARREG_ANGLE(close, timeperiod=period)
        
        return df
    
    def _calculate_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate momentum indicators (50+)"""
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        volume = df['volume'].values
        
        # RSI variations
        for period in [6, 9, 14, 21, 28]:
            df[f'rsi_{period}'] = talib.RSI(close, timeperiod=period)
        
        # Stochastic
        for k, d in [(5, 3), (14, 3), (21, 5)]:
            slowk, slowd = talib.STOCH(high, low, close, 
                                       fastk_period=k, slowk_period=3, slowd_period=d)
            df[f'stoch_k_{k}'] = slowk
            df[f'stoch_d_{k}'] = slowd
        
        # Stochastic RSI
        df['stochrsi_k'], df['stochrsi_d'] = talib.STOCHRSI(close, timeperiod=14)
        
        # Williams %R
        for period in [7, 14, 21]:
            df[f'willr_{period}'] = talib.WILLR(high, low, close, timeperiod=period)
        
        # CCI (Commodity Channel Index)
        for period in [14, 20, 30]:
            df[f'cci_{period}'] = talib.CCI(high, low, close, timeperiod=period)
        
        # ROC (Rate of Change)
        for period in [10, 20, 30]:
            df[f'roc_{period}'] = talib.ROC(close, timeperiod=period)
            df[f'rocp_{period}'] = talib.ROCP(close, timeperiod=period)
        
        # CMO (Chande Momentum Oscillator)
        for period in [9, 14, 20]:
            df[f'cmo_{period}'] = talib.CMO(close, timeperiod=period)
        
        # MFI (Money Flow Index)
        df['mfi_14'] = talib.MFI(high, low, close, volume, timeperiod=14)
        
        # Ultimate Oscillator
        df['ultosc'] = talib.ULTOSC(high, low, close)
        
        # Awesome Oscillator
        df.ta.ao(append=True)
        
        # Percentage Price Oscillator
        df['ppo'] = talib.PPO(close)
        
        # Balance of Power
        df['bop'] = talib.BOP(df['open'].values, high, low, close)
        
        # TRIX
        df['trix'] = talib.TRIX(close, timeperiod=14)
        
        return df
    
    def _calculate_volatility_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate volatility indicators (40+)"""
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        
        # Bollinger Bands variations
        for period, std in [(20, 2), (20, 3), (50, 2)]:
            upper, middle, lower = talib.BBANDS(close, timeperiod=period, 
                                                 nbdevup=std, nbdevdn=std)
            df[f'bb_upper_{period}_{std}'] = upper
            df[f'bb_middle_{period}_{std}'] = middle
            df[f'bb_lower_{period}_{std}'] = lower
            df[f'bb_width_{period}_{std}'] = (upper - lower) / middle
            df[f'bb_pct_{period}_{std}'] = (close - lower) / (upper - lower)
        
        # ATR (Average True Range)
        for period in [7, 14, 21, 30]:
            df[f'atr_{period}'] = talib.ATR(high, low, close, timeperiod=period)
            df[f'natr_{period}'] = talib.NATR(high, low, close, timeperiod=period)
        
        # Keltner Channels
        for period in [20, 50]:
            df.ta.kc(length=period, append=True)
        
        # Donchian Channels
        for period in [20, 50]:
            df.ta.donchian(length=period, append=True)
        
        # Standard Deviation
        for period in [10, 20, 30]:
            df[f'stddev_{period}'] = talib.STDDEV(close, timeperiod=period)
        
        # Historical Volatility
        for period in [10, 20, 30, 50]:
            returns = np.log(close / np.roll(close, 1))
            df[f'hist_vol_{period}'] = pd.Series(returns).rolling(period).std() * np.sqrt(252)
        
        # True Range
        df['tr'] = talib.TRANGE(high, low, close)
        
        return df
    
    def _calculate_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate volume indicators (30+)"""
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        volume = df['volume'].values
        
        # OBV (On Balance Volume)
        df['obv'] = talib.OBV(close, volume)
        
        # Volume Moving Averages
        for period in [10, 20, 50]:
            df[f'vol_sma_{period}'] = talib.SMA(volume, timeperiod=period)
            df[f'vol_ratio_{period}'] = volume / df[f'vol_sma_{period}']
        
        # VWAP (Volume Weighted Average Price)
        df['vwap'] = (close * volume).cumsum() / volume.cumsum()
        
        # AD (Accumulation/Distribution)
        df['ad'] = talib.AD(high, low, close, volume)
        
        # ADOsc (Chaikin A/D Oscillator)
        df['adosc'] = talib.ADOSC(high, low, close, volume)
        
        # CMF (Chaikin Money Flow)
        df.ta.cmf(append=True)
        
        # Force Index
        df.ta.efi(append=True)
        
        # Volume Price Trend
        df.ta.pvt(append=True)
        
        # Negative Volume Index
        df.ta.nvi(append=True)
        
        # Positive Volume Index
        df.ta.pvi(append=True)
        
        return df
    
    def _calculate_support_resistance(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate support/resistance levels (20+)"""
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        
        # Pivot Points
        df['pivot'] = (high + low + close) / 3
        df['r1'] = 2 * df['pivot'] - low
        df['r2'] = df['pivot'] + (high - low)
        df['r3'] = high + 2 * (df['pivot'] - low)
        df['s1'] = 2 * df['pivot'] - high
        df['s2'] = df['pivot'] - (high - low)
        df['s3'] = low - 2 * (high - df['pivot'])
        
        # Fibonacci Retracement levels
        window = 50
        df['fib_high'] = pd.Series(high).rolling(window).max()
        df['fib_low'] = pd.Series(low).rolling(window).min()
        diff = df['fib_high'] - df['fib_low']
        
        for level in [0.236, 0.382, 0.5, 0.618, 0.786]:
            df[f'fib_{level}'] = df['fib_low'] + diff * level
        
        return df
    
    def _calculate_pattern_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate pattern recognition indicators (30+)"""
        open_price = df['open'].values
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values
        
        # Candlestick patterns
        patterns = [
            'CDL2CROWS', 'CDL3BLACKCROWS', 'CDL3INSIDE', 'CDL3LINESTRIKE',
            'CDL3OUTSIDE', 'CDL3STARSINSOUTH', 'CDL3WHITESOLDIERS',
            'CDLABANDONEDBABY', 'CDLADVANCEBLOCK', 'CDLBELTHOLD',
            'CDLBREAKAWAY', 'CDLCLOSINGMARUBOZU', 'CDLCONCEALBABYSWALL',
            'CDLCOUNTERATTACK', 'CDLDARKCLOUDCOVER', 'CDLDOJI',
            'CDLDOJISTAR', 'CDLDRAGONFLYDOJI', 'CDLENGULFING',
            'CDLEVENINGDOJISTAR', 'CDLEVENINGSTAR', 'CDLGAPSIDESIDEWHITE',
            'CDLGRAVESTONEDOJI', 'CDLHAMMER', 'CDLHANGINGMAN',
            'CDLHARAMI', 'CDLHARAMICROSS', 'CDLHIGHWAVE',
            'CDLHIKKAKE', 'CDLHIKKAKEMOD', 'CDLHOMINGPIGEON'
        ]
        
        for pattern in patterns:
            func = getattr(talib, pattern)
            df[pattern.lower()] = func(open_price, high, low, close)
        
        return df
    
    def _calculate_statistical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate statistical indicators (20+)"""
        close = df['close'].values
        
        # Returns
        df['returns'] = close / np.roll(close, 1) - 1
        df['log_returns'] = np.log(close / np.roll(close, 1))
        
        # Rolling statistics
        for period in [10, 20, 50]:
            returns_series = pd.Series(df['returns'])
            df[f'mean_{period}'] = returns_series.rolling(period).mean()
            df[f'std_{period}'] = returns_series.rolling(period).std()
            df[f'skew_{period}'] = returns_series.rolling(period).skew()
            df[f'kurt_{period}'] = returns_series.rolling(period).kurt()
            df[f'var_{period}'] = returns_series.rolling(period).var()
        
        # Z-Score
        for period in [20, 50]:
            mean = pd.Series(close).rolling(period).mean()
            std = pd.Series(close).rolling(period).std()
            df[f'zscore_{period}'] = (close - mean) / std
        
        # Correlation with volume
        for period in [20, 50]:
            df[f'price_vol_corr_{period}'] = pd.Series(close).rolling(period).corr(
                pd.Series(df['volume'].values)
            )
        
        return df
    
    def _calculate_custom_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate custom indicators (10+)"""
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        volume = df['volume'].values
        
        # Price momentum
        for period in [1, 5, 10, 20]:
            df[f'momentum_{period}'] = close / np.roll(close, period) - 1
        
        # Volume momentum
        for period in [5, 10, 20]:
            df[f'vol_momentum_{period}'] = volume / np.roll(volume, period) - 1
        
        # Range indicators
        df['high_low_ratio'] = high / low
        df['close_open_ratio'] = close / df['open'].values
        
        # Composite indicators
        df['bull_bear_power'] = df['rsi_14'] + df['macd_12_26']
        df['trend_strength'] = df['adx_14'] * np.sign(df['macd_12_26'])
        
        return df
    
    def get_feature_importance_ready(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for ML models
        
        Args:
            df: DataFrame with all indicators
            
        Returns:
            Cleaned DataFrame ready for ML
        """
        # Remove NaN values
        df = df.fillna(method='bfill').fillna(method='ffill')
        
        # Remove infinite values
        df = df.replace([np.inf, -np.inf], np.nan).fillna(0)
        
        return df

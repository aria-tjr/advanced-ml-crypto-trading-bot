"""
Unified Exchange Interface
Abstract base class for all exchange implementations
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd


class BaseExchange(ABC):
    """Abstract base class for cryptocurrency exchange clients"""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, 
                 testnet: bool = True):
        """
        Initialize exchange client
        
        Args:
            api_key: API key
            api_secret: API secret
            testnet: Use testnet environment
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.client = None
        
    @abstractmethod
    async def connect(self) -> None:
        """Connect to exchange"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from exchange"""
        pass
    
    @abstractmethod
    async def get_balance(self) -> Dict[str, float]:
        """
        Get account balance
        
        Returns:
            Dictionary of asset balances
        """
        pass
    
    @abstractmethod
    async def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get open positions
        
        Returns:
            List of position dictionaries
        """
        pass
    
    @abstractmethod
    async def get_historical_data(self, symbol: str, timeframe: str, 
                                   start_time: Optional[datetime] = None,
                                   end_time: Optional[datetime] = None,
                                   limit: int = 1000) -> pd.DataFrame:
        """
        Get historical OHLCV data
        
        Args:
            symbol: Trading pair symbol
            timeframe: Candlestick interval
            start_time: Start time
            end_time: End time
            limit: Maximum number of candles
            
        Returns:
            DataFrame with OHLCV data
        """
        pass
    
    @abstractmethod
    async def place_order(self, symbol: str, side: str, order_type: str,
                         quantity: float, price: Optional[float] = None,
                         leverage: Optional[int] = None,
                         stop_loss: Optional[float] = None,
                         take_profit: Optional[float] = None) -> Dict[str, Any]:
        """
        Place an order
        
        Args:
            symbol: Trading pair
            side: BUY or SELL
            order_type: LIMIT, MARKET, etc.
            quantity: Order quantity
            price: Order price (for limit orders)
            leverage: Leverage multiplier
            stop_loss: Stop loss price
            take_profit: Take profit price
            
        Returns:
            Order result dictionary
        """
        pass
    
    @abstractmethod
    async def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """
        Cancel an order
        
        Args:
            symbol: Trading pair
            order_id: Order ID
            
        Returns:
            Cancellation result
        """
        pass
    
    @abstractmethod
    async def get_order_status(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """
        Get order status
        
        Args:
            symbol: Trading pair
            order_id: Order ID
            
        Returns:
            Order status dictionary
        """
        pass
    
    @abstractmethod
    async def set_leverage(self, symbol: str, leverage: int) -> Dict[str, Any]:
        """
        Set leverage for symbol
        
        Args:
            symbol: Trading pair
            leverage: Leverage multiplier
            
        Returns:
            Result dictionary
        """
        pass
    
    @abstractmethod
    async def get_ticker(self, symbol: str) -> Dict[str, float]:
        """
        Get current ticker data
        
        Args:
            symbol: Trading pair
            
        Returns:
            Ticker data dictionary
        """
        pass
    
    @abstractmethod
    async def get_orderbook(self, symbol: str, limit: int = 20) -> Dict[str, List]:
        """
        Get orderbook data
        
        Args:
            symbol: Trading pair
            limit: Depth limit
            
        Returns:
            Orderbook with bids and asks
        """
        pass

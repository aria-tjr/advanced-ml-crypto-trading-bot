"""
Binance Futures Exchange Client
Implementation of Binance futures trading
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
import ccxt
from binance.client import Client
from binance import AsyncClient, BinanceSocketManager
import asyncio
from bot.exchanges.base import BaseExchange
from loguru import logger


class BinanceExchange(BaseExchange):
    """Binance Futures exchange implementation"""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None,
                 testnet: bool = True):
        super().__init__(api_key, api_secret, testnet)
        self.exchange_id = 'binance'
        self.ccxt_client = None
        
    async def connect(self) -> None:
        """Connect to Binance"""
        try:
            # Initialize CCXT client for futures
            self.ccxt_client = ccxt.binance({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future',
                    'test': self.testnet
                }
            })
            
            if self.testnet:
                self.ccxt_client.set_sandbox_mode(True)
                
            # Initialize async client
            self.client = await AsyncClient.create(
                api_key=self.api_key,
                api_secret=self.api_secret,
                testnet=self.testnet
            )
            
            logger.info(f"Connected to Binance (testnet={self.testnet})")
            
        except Exception as e:
            logger.error(f"Failed to connect to Binance: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from Binance"""
        if self.client:
            await self.client.close_connection()
            logger.info("Disconnected from Binance")
    
    async def get_balance(self) -> Dict[str, float]:
        """Get futures account balance"""
        try:
            account = await self.client.futures_account()
            balances = {}
            
            for asset in account['assets']:
                if float(asset['walletBalance']) > 0:
                    balances[asset['asset']] = {
                        'free': float(asset['availableBalance']),
                        'used': float(asset['initialMargin']),
                        'total': float(asset['walletBalance'])
                    }
            
            return balances
            
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return {}
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get open futures positions"""
        try:
            positions = await self.client.futures_position_information()
            open_positions = []
            
            for pos in positions:
                position_amt = float(pos['positionAmt'])
                if position_amt != 0:
                    open_positions.append({
                        'symbol': pos['symbol'],
                        'side': 'LONG' if position_amt > 0 else 'SHORT',
                        'size': abs(position_amt),
                        'entry_price': float(pos['entryPrice']),
                        'unrealized_pnl': float(pos['unRealizedProfit']),
                        'leverage': int(pos['leverage']),
                        'liquidation_price': float(pos['liquidationPrice'])
                    })
            
            return open_positions
            
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    async def get_historical_data(self, symbol: str, timeframe: str,
                                   start_time: Optional[datetime] = None,
                                   end_time: Optional[datetime] = None,
                                   limit: int = 1000) -> pd.DataFrame:
        """Get historical OHLCV data"""
        try:
            if start_time:
                start_ms = int(start_time.timestamp() * 1000)
            else:
                start_ms = None
                
            if end_time:
                end_ms = int(end_time.timestamp() * 1000)
            else:
                end_ms = None
            
            klines = await self.client.futures_klines(
                symbol=symbol,
                interval=timeframe,
                startTime=start_ms,
                endTime=end_ms,
                limit=limit
            )
            
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            return df[['open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return pd.DataFrame()
    
    async def place_order(self, symbol: str, side: str, order_type: str,
                         quantity: float, price: Optional[float] = None,
                         leverage: Optional[int] = None,
                         stop_loss: Optional[float] = None,
                         take_profit: Optional[float] = None) -> Dict[str, Any]:
        """Place futures order"""
        try:
            if leverage:
                await self.set_leverage(symbol, leverage)
            
            params = {
                'symbol': symbol,
                'side': side,
                'type': order_type,
                'quantity': quantity
            }
            
            if order_type == 'LIMIT':
                params['price'] = price
                params['timeInForce'] = 'GTC'
            
            order = await self.client.futures_create_order(**params)
            
            # Place stop loss and take profit orders if specified
            if stop_loss:
                await self._place_stop_loss(symbol, side, quantity, stop_loss)
            
            if take_profit:
                await self._place_take_profit(symbol, side, quantity, take_profit)
            
            return order
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            raise
    
    async def _place_stop_loss(self, symbol: str, side: str, quantity: float, 
                               stop_price: float) -> Dict[str, Any]:
        """Place stop loss order"""
        stop_side = 'SELL' if side == 'BUY' else 'BUY'
        
        return await self.client.futures_create_order(
            symbol=symbol,
            side=stop_side,
            type='STOP_MARKET',
            stopPrice=stop_price,
            quantity=quantity
        )
    
    async def _place_take_profit(self, symbol: str, side: str, quantity: float,
                                 price: float) -> Dict[str, Any]:
        """Place take profit order"""
        tp_side = 'SELL' if side == 'BUY' else 'BUY'
        
        return await self.client.futures_create_order(
            symbol=symbol,
            side=tp_side,
            type='TAKE_PROFIT_MARKET',
            stopPrice=price,
            quantity=quantity
        )
    
    async def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """Cancel order"""
        try:
            return await self.client.futures_cancel_order(
                symbol=symbol,
                orderId=order_id
            )
        except Exception as e:
            logger.error(f"Error canceling order: {e}")
            raise
    
    async def get_order_status(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """Get order status"""
        try:
            return await self.client.futures_get_order(
                symbol=symbol,
                orderId=order_id
            )
        except Exception as e:
            logger.error(f"Error getting order status: {e}")
            raise
    
    async def set_leverage(self, symbol: str, leverage: int) -> Dict[str, Any]:
        """Set leverage"""
        try:
            return await self.client.futures_change_leverage(
                symbol=symbol,
                leverage=leverage
            )
        except Exception as e:
            logger.error(f"Error setting leverage: {e}")
            raise
    
    async def get_ticker(self, symbol: str) -> Dict[str, float]:
        """Get ticker data"""
        try:
            ticker = await self.client.futures_ticker(symbol=symbol)
            return {
                'last_price': float(ticker['lastPrice']),
                'bid': float(ticker['bidPrice']),
                'ask': float(ticker['askPrice']),
                'volume': float(ticker['volume']),
                'change': float(ticker['priceChangePercent'])
            }
        except Exception as e:
            logger.error(f"Error getting ticker: {e}")
            return {}
    
    async def get_orderbook(self, symbol: str, limit: int = 20) -> Dict[str, List]:
        """Get orderbook"""
        try:
            orderbook = await self.client.futures_order_book(
                symbol=symbol,
                limit=limit
            )
            
            return {
                'bids': [[float(price), float(qty)] for price, qty in orderbook['bids']],
                'asks': [[float(price), float(qty)] for price, qty in orderbook['asks']],
                'timestamp': orderbook['E']
            }
        except Exception as e:
            logger.error(f"Error getting orderbook: {e}")
            return {'bids': [], 'asks': []}

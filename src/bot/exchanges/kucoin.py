"""
KuCoin Futures Exchange Client
Implementation of KuCoin futures trading
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
import ccxt
from bot.exchanges.base import BaseExchange
from loguru import logger


class KuCoinExchange(BaseExchange):
    """KuCoin Futures exchange implementation"""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None,
                 passphrase: Optional[str] = None, testnet: bool = True):
        super().__init__(api_key, api_secret, testnet)
        self.passphrase = passphrase
        self.exchange_id = 'kucoin'
        
    async def connect(self) -> None:
        """Connect to KuCoin"""
        try:
            self.client = ccxt.kucoinfutures({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'password': self.passphrase,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future'
                }
            })
            
            if self.testnet:
                self.client.set_sandbox_mode(True)
            
            logger.info(f"Connected to KuCoin (testnet={self.testnet})")
        except Exception as e:
            logger.error(f"Failed to connect to KuCoin: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from KuCoin"""
        if self.client:
            await self.client.close()
        logger.info("Disconnected from KuCoin")
    
    async def get_balance(self) -> Dict[str, float]:
        """Get account balance"""
        try:
            balance = self.client.fetch_balance()
            balances = {}
            
            for currency, amount in balance['total'].items():
                if amount > 0:
                    balances[currency] = {
                        'free': balance['free'].get(currency, 0),
                        'used': balance['used'].get(currency, 0),
                        'total': amount
                    }
            
            return balances
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return {}
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get open positions"""
        try:
            positions = self.client.fetch_positions()
            open_positions = []
            
            for pos in positions:
                if pos['contracts'] > 0:
                    open_positions.append({
                        'symbol': pos['symbol'],
                        'side': pos['side'],
                        'size': pos['contracts'],
                        'entry_price': pos['entryPrice'],
                        'unrealized_pnl': pos['unrealizedPnl'],
                        'leverage': pos['leverage'],
                        'liquidation_price': pos.get('liquidationPrice', 0)
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
            since = int(start_time.timestamp() * 1000) if start_time else None
            
            ohlcv = self.client.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                since=since,
                limit=limit
            )
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return pd.DataFrame()
    
    async def place_order(self, symbol: str, side: str, order_type: str,
                         quantity: float, price: Optional[float] = None,
                         leverage: Optional[int] = None,
                         stop_loss: Optional[float] = None,
                         take_profit: Optional[float] = None) -> Dict[str, Any]:
        """Place order"""
        try:
            if leverage:
                await self.set_leverage(symbol, leverage)
            
            params = {}
            if stop_loss:
                params['stopLoss'] = {'price': stop_loss}
            if take_profit:
                params['takeProfit'] = {'price': take_profit}
            
            order = self.client.create_order(
                symbol=symbol,
                type=order_type.lower(),
                side=side.lower(),
                amount=quantity,
                price=price,
                params=params
            )
            
            return order
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            raise
    
    async def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """Cancel order"""
        try:
            return self.client.cancel_order(order_id, symbol)
        except Exception as e:
            logger.error(f"Error canceling order: {e}")
            raise
    
    async def get_order_status(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """Get order status"""
        try:
            return self.client.fetch_order(order_id, symbol)
        except Exception as e:
            logger.error(f"Error getting order status: {e}")
            raise
    
    async def set_leverage(self, symbol: str, leverage: int) -> Dict[str, Any]:
        """Set leverage"""
        try:
            return self.client.set_leverage(leverage, symbol)
        except Exception as e:
            logger.error(f"Error setting leverage: {e}")
            raise
    
    async def get_ticker(self, symbol: str) -> Dict[str, float]:
        """Get ticker data"""
        try:
            ticker = self.client.fetch_ticker(symbol)
            return {
                'last_price': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'volume': ticker['baseVolume'],
                'change': ticker['percentage']
            }
        except Exception as e:
            logger.error(f"Error getting ticker: {e}")
            return {}
    
    async def get_orderbook(self, symbol: str, limit: int = 20) -> Dict[str, List]:
        """Get orderbook"""
        try:
            orderbook = self.client.fetch_order_book(symbol, limit)
            return {
                'bids': orderbook['bids'],
                'asks': orderbook['asks'],
                'timestamp': orderbook['timestamp']
            }
        except Exception as e:
            logger.error(f"Error getting orderbook: {e}")
            return {'bids': [], 'asks': []}

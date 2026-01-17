"""
Bybit Futures Exchange Client
Implementation of Bybit futures trading
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
from pybit.unified_trading import HTTP
import ccxt
from bot.exchanges.base import BaseExchange
from loguru import logger


class BybitExchange(BaseExchange):
    """Bybit Futures exchange implementation"""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None,
                 testnet: bool = True):
        super().__init__(api_key, api_secret, testnet)
        self.exchange_id = 'bybit'
        
    async def connect(self) -> None:
        """Connect to Bybit"""
        try:
            self.client = HTTP(
                testnet=self.testnet,
                api_key=self.api_key,
                api_secret=self.api_secret
            )
            logger.info(f"Connected to Bybit (testnet={self.testnet})")
        except Exception as e:
            logger.error(f"Failed to connect to Bybit: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from Bybit"""
        self.client = None
        logger.info("Disconnected from Bybit")
    
    async def get_balance(self) -> Dict[str, float]:
        """Get account balance"""
        try:
            response = self.client.get_wallet_balance(accountType="UNIFIED")
            balances = {}
            
            if response['retCode'] == 0:
                for coin in response['result']['list'][0]['coin']:
                    if float(coin['walletBalance']) > 0:
                        balances[coin['coin']] = {
                            'free': float(coin['availableToWithdraw']),
                            'used': float(coin['locked']),
                            'total': float(coin['walletBalance'])
                        }
            
            return balances
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return {}
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get open positions"""
        try:
            response = self.client.get_positions(
                category="linear",
                settleCoin="USDT"
            )
            
            open_positions = []
            if response['retCode'] == 0:
                for pos in response['result']['list']:
                    size = float(pos['size'])
                    if size > 0:
                        open_positions.append({
                            'symbol': pos['symbol'],
                            'side': pos['side'],
                            'size': size,
                            'entry_price': float(pos['avgPrice']),
                            'unrealized_pnl': float(pos['unrealisedPnl']),
                            'leverage': int(float(pos['leverage'])),
                            'liquidation_price': float(pos['liqPrice']) if pos['liqPrice'] else 0
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
            params = {
                'category': 'linear',
                'symbol': symbol,
                'interval': timeframe,
                'limit': limit
            }
            
            if start_time:
                params['start'] = int(start_time.timestamp() * 1000)
            if end_time:
                params['end'] = int(end_time.timestamp() * 1000)
            
            response = self.client.get_kline(**params)
            
            if response['retCode'] == 0:
                data = response['result']['list']
                df = pd.DataFrame(data, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'
                ])
                
                df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms')
                df.set_index('timestamp', inplace=True)
                
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = df[col].astype(float)
                
                return df[['open', 'high', 'low', 'close', 'volume']].sort_index()
            
            return pd.DataFrame()
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
            
            params = {
                'category': 'linear',
                'symbol': symbol,
                'side': side.capitalize(),
                'orderType': order_type.capitalize(),
                'qty': str(quantity)
            }
            
            if order_type == 'LIMIT' and price:
                params['price'] = str(price)
            
            if stop_loss:
                params['stopLoss'] = str(stop_loss)
            
            if take_profit:
                params['takeProfit'] = str(take_profit)
            
            response = self.client.place_order(**params)
            return response
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            raise
    
    async def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """Cancel order"""
        try:
            response = self.client.cancel_order(
                category='linear',
                symbol=symbol,
                orderId=order_id
            )
            return response
        except Exception as e:
            logger.error(f"Error canceling order: {e}")
            raise
    
    async def get_order_status(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """Get order status"""
        try:
            response = self.client.get_order_history(
                category='linear',
                symbol=symbol,
                orderId=order_id
            )
            return response
        except Exception as e:
            logger.error(f"Error getting order status: {e}")
            raise
    
    async def set_leverage(self, symbol: str, leverage: int) -> Dict[str, Any]:
        """Set leverage"""
        try:
            response = self.client.set_leverage(
                category='linear',
                symbol=symbol,
                buyLeverage=str(leverage),
                sellLeverage=str(leverage)
            )
            return response
        except Exception as e:
            logger.error(f"Error setting leverage: {e}")
            raise
    
    async def get_ticker(self, symbol: str) -> Dict[str, float]:
        """Get ticker data"""
        try:
            response = self.client.get_tickers(
                category='linear',
                symbol=symbol
            )
            
            if response['retCode'] == 0:
                ticker = response['result']['list'][0]
                return {
                    'last_price': float(ticker['lastPrice']),
                    'bid': float(ticker['bid1Price']),
                    'ask': float(ticker['ask1Price']),
                    'volume': float(ticker['volume24h']),
                    'change': float(ticker['price24hPcnt'])
                }
            return {}
        except Exception as e:
            logger.error(f"Error getting ticker: {e}")
            return {}
    
    async def get_orderbook(self, symbol: str, limit: int = 20) -> Dict[str, List]:
        """Get orderbook"""
        try:
            response = self.client.get_orderbook(
                category='linear',
                symbol=symbol,
                limit=limit
            )
            
            if response['retCode'] == 0:
                orderbook = response['result']
                return {
                    'bids': [[float(price), float(qty)] for price, qty in orderbook['b']],
                    'asks': [[float(price), float(qty)] for price, qty in orderbook['a']],
                    'timestamp': orderbook['ts']
                }
            return {'bids': [], 'asks': []}
        except Exception as e:
            logger.error(f"Error getting orderbook: {e}")
            return {'bids': [], 'asks': []}

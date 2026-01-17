"""
Main Trading Bot
Orchestrates all components for automated trading
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from loguru import logger

from bot.config import Config, load_config
from bot.exchanges.binance import BinanceExchange
from bot.exchanges.bybit import BybitExchange
from bot.exchanges.kucoin import KuCoinExchange
from bot.data.pipeline import DataPipeline
from bot.models.xgboost_model import XGBoostModel
from bot.models.lstm_model import LSTMModel
from bot.models.transformer_model import TransformerModel
from bot.strategy.regime_detection import MarketRegimeDetector
from bot.risk.risk_manager import RiskManager
from bot.backtest.backtest_engine import BacktestEngine


class TradingBot:
    """Main trading bot orchestrator"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize trading bot
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = load_config(config_path)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize components
        self.exchange = None
        self.data_pipeline = None
        self.models = {}
        self.regime_detector = MarketRegimeDetector()
        self.risk_manager = RiskManager(
            max_position_size=self.config.risk.max_position_size,
            stop_loss_pct=self.config.risk.stop_loss_pct,
            take_profit_pct=self.config.risk.take_profit_pct,
            max_daily_loss=self.config.risk.max_daily_loss,
            risk_per_trade=self.config.risk.risk_per_trade,
            use_kelly=self.config.risk.use_kelly_criterion
        )
        
        self.is_running = False
        self.positions = {}
        self.account_balance = 0.0
        
        logger.info("Trading bot initialized")
    
    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        log_path = self.config.logs_dir / f"trading_bot_{datetime.now().strftime('%Y%m%d')}.log"
        self.config.logs_dir.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_path,
            rotation="1 day",
            retention="30 days",
            level="INFO"
        )
    
    async def initialize(self) -> None:
        """Initialize exchange connection and components"""
        logger.info("Initializing trading bot...")
        
        # Initialize exchange
        exchange_name = self.config.exchange.name.lower()
        
        if exchange_name == 'binance':
            self.exchange = BinanceExchange(
                api_key=self.config.exchange.api_key,
                api_secret=self.config.exchange.api_secret,
                testnet=self.config.exchange.testnet
            )
        elif exchange_name == 'bybit':
            self.exchange = BybitExchange(
                api_key=self.config.exchange.api_key,
                api_secret=self.config.exchange.api_secret,
                testnet=self.config.exchange.testnet
            )
        elif exchange_name == 'kucoin':
            self.exchange = KuCoinExchange(
                api_key=self.config.exchange.api_key,
                api_secret=self.config.exchange.api_secret,
                testnet=self.config.exchange.testnet
            )
        else:
            raise ValueError(f"Unsupported exchange: {exchange_name}")
        
        await self.exchange.connect()
        
        # Initialize data pipeline
        self.data_pipeline = DataPipeline(
            exchange=self.exchange,
            symbols=self.config.trading.symbols,
            timeframe=self.config.trading.timeframe
        )
        
        # Initialize ML models
        self._initialize_models()
        
        # Get account balance
        balance = await self.exchange.get_balance()
        self.account_balance = sum([b['total'] for b in balance.values()])
        
        logger.info(f"Bot initialized. Account balance: ${self.account_balance:.2f}")
    
    def _initialize_models(self) -> None:
        """Initialize ML models"""
        model_type = self.config.ml.model_type
        
        if model_type == 'xgboost' or model_type == 'ensemble':
            self.models['xgboost'] = XGBoostModel(
                lookback_period=self.config.ml.lookback_period,
                prediction_horizon=self.config.ml.prediction_horizon
            )
        
        if model_type == 'lstm' or model_type == 'ensemble':
            self.models['lstm'] = LSTMModel(
                lookback_period=self.config.ml.lookback_period,
                prediction_horizon=self.config.ml.prediction_horizon
            )
        
        if model_type == 'transformer' or model_type == 'ensemble':
            self.models['transformer'] = TransformerModel(
                lookback_period=self.config.ml.lookback_period,
                prediction_horizon=self.config.ml.prediction_horizon
            )
        
        logger.info(f"Initialized {len(self.models)} ML models")
    
    async def train_models(self, symbol: str) -> None:
        """
        Train ML models on historical data
        
        Args:
            symbol: Trading symbol
        """
        logger.info(f"Training models for {symbol}")
        
        # Fetch and prepare data
        df = await self.data_pipeline.prepare_training_data(symbol)
        
        if df.empty:
            logger.error(f"No data available for training {symbol}")
            return
        
        # Train each model
        for model_name, model in self.models.items():
            try:
                logger.info(f"Training {model_name}...")
                
                if model_name == 'xgboost':
                    X, y = model.prepare_data(df)
                    metrics = model.train(X, y)
                    logger.info(f"XGBoost metrics: {metrics}")
                
                elif model_name in ['lstm', 'transformer']:
                    X, y = model.prepare_data(df)
                    history = model.train(X, y, epochs=50)
                    logger.info(f"{model_name} training complete")
                
                # Save model
                model_path = self.config.models_dir / 'saved' / symbol
                model.save(model_path)
                
            except Exception as e:
                logger.error(f"Error training {model_name}: {e}")
    
    async def generate_signals(self, symbol: str) -> Dict:
        """
        Generate trading signals using ML models
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dictionary with signals and confidence
        """
        # Get latest features
        df = await self.data_pipeline.get_latest_features(symbol)
        
        if df.empty:
            return {'signal': 0, 'confidence': 0.0}
        
        # Detect market regime
        df_with_regime = self.regime_detector.calculate_regime_features(df)
        regime_id, regime_name = self.regime_detector.get_current_regime(df_with_regime)
        
        # Get predictions from all models
        predictions = []
        
        for model_name, model in self.models.items():
            try:
                if hasattr(model, 'predict'):
                    pred = model.predict(df.values)
                    predictions.append(pred[0] if hasattr(pred, '__iter__') else pred)
            except Exception as e:
                logger.error(f"Error getting prediction from {model_name}: {e}")
        
        # Ensemble prediction
        if predictions:
            avg_prediction = sum(predictions) / len(predictions)
            signal = 1 if avg_prediction > 0.001 else (-1 if avg_prediction < -0.001 else 0)
            confidence = abs(avg_prediction) * 10  # Scale to 0-1
        else:
            signal = 0
            confidence = 0.0
        
        return {
            'signal': signal,
            'confidence': min(confidence, 1.0),
            'prediction': avg_prediction if predictions else 0,
            'regime': regime_name
        }
    
    async def execute_trade(self, symbol: str, signal: Dict) -> None:
        """
        Execute trade based on signal
        
        Args:
            symbol: Trading symbol
            signal: Trading signal dictionary
        """
        # Check if should take trade
        if not self.risk_manager.should_take_trade(
            signal['confidence'],
            signal['regime'],
            self.account_balance,
            len(self.positions)
        ):
            logger.info(f"Trade rejected by risk manager for {symbol}")
            return
        
        # Get current price
        ticker = await self.exchange.get_ticker(symbol)
        current_price = ticker['last_price']
        
        # Calculate position size
        position_size = self.risk_manager.calculate_position_size(
            account_balance=self.account_balance,
            entry_price=current_price,
            stop_loss_price=current_price * (1 - self.config.risk.stop_loss_pct)
        )
        
        # Calculate stop loss and take profit
        side = 'BUY' if signal['signal'] > 0 else 'SELL'
        stop_loss = self.risk_manager.calculate_stop_loss(current_price, side)
        take_profit = self.risk_manager.calculate_take_profit(current_price, side)
        
        # Place order
        try:
            order = await self.exchange.place_order(
                symbol=symbol,
                side=side,
                order_type=self.config.trading.order_type,
                quantity=position_size / current_price,
                price=current_price if self.config.trading.order_type == 'LIMIT' else None,
                leverage=self.config.trading.leverage,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
            logger.info(f"Order placed: {order}")
            
            # Track position
            self.positions[symbol] = {
                'side': side,
                'size': position_size / current_price,
                'entry_price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'order_id': order.get('orderId', order.get('id'))
            }
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
    
    async def run_strategy(self) -> None:
        """Run trading strategy loop"""
        self.is_running = True
        
        logger.info("Starting trading strategy...")
        
        while self.is_running:
            try:
                # Update account balance
                balance = await self.exchange.get_balance()
                self.account_balance = sum([b['total'] for b in balance.values()])
                
                # Check positions
                positions = await self.exchange.get_positions()
                logger.info(f"Open positions: {len(positions)}")
                
                # Generate signals for each symbol
                for symbol in self.config.trading.symbols:
                    signal = await self.generate_signals(symbol)
                    
                    logger.info(f"{symbol}: Signal={signal['signal']}, "
                              f"Confidence={signal['confidence']:.2f}, "
                              f"Regime={signal['regime']}")
                    
                    # Execute trade if signal is strong
                    if abs(signal['signal']) > 0 and signal['confidence'] > 0.6:
                        await self.execute_trade(symbol, signal)
                
                # Wait before next iteration
                await asyncio.sleep(60 * 60)  # 1 hour
                
            except Exception as e:
                logger.error(f"Error in strategy loop: {e}")
                await asyncio.sleep(60)
    
    async def run_backtest(self, symbol: str, start_date: str, end_date: str) -> Dict:
        """
        Run backtest on historical data
        
        Args:
            symbol: Trading symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Backtest results
        """
        logger.info(f"Running backtest for {symbol} from {start_date} to {end_date}")
        
        # Fetch data
        df = await self.data_pipeline.fetch_historical_data(
            symbol,
            start_date=datetime.strptime(start_date, '%Y-%m-%d')
        )
        
        # Calculate features
        df = self.data_pipeline.calculate_features(df)
        
        # Generate signals (simplified for backtest)
        # In production, would use actual model predictions
        signals = (df['rsi_14'] < 30).astype(int) - (df['rsi_14'] > 70).astype(int)
        
        # Run backtest
        engine = BacktestEngine(
            initial_capital=self.config.backtest.initial_capital,
            commission=self.config.backtest.commission,
            slippage=self.config.backtest.slippage
        )
        
        results = engine.run_backtest(df, signals)
        
        return results
    
    async def shutdown(self) -> None:
        """Shutdown bot gracefully"""
        logger.info("Shutting down trading bot...")
        
        self.is_running = False
        
        if self.exchange:
            await self.exchange.disconnect()
        
        logger.info("Bot shutdown complete")


def main():
    """Main entry point"""
    bot = TradingBot()
    
    try:
        asyncio.run(bot.initialize())
        asyncio.run(bot.run_strategy())
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        asyncio.run(bot.shutdown())
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        asyncio.run(bot.shutdown())


if __name__ == '__main__':
    main()

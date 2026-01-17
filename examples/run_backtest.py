"""
Example: Run Backtest
Demonstrates how to run a backtest on historical data
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from bot.config import load_config
from bot.exchanges.binance import BinanceExchange
from bot.data.pipeline import DataPipeline
from bot.backtest.backtest_engine import BacktestEngine
from bot.strategy.regime_detection import MarketRegimeDetector
from loguru import logger


async def run_backtest():
    """Run backtest example"""
    
    # Load configuration
    config = load_config('config/config.yaml')
    
    # Initialize exchange
    exchange = BinanceExchange(testnet=True)
    await exchange.connect()
    
    # Initialize data pipeline
    pipeline = DataPipeline(
        exchange=exchange,
        symbols=['BTCUSDT'],
        timeframe='1h',
        lookback_days=180
    )
    
    # Fetch data
    logger.info("Fetching historical data...")
    df = await pipeline.fetch_historical_data('BTCUSDT')
    
    if df.empty:
        logger.error("No data available")
        await exchange.disconnect()
        return
    
    # Calculate features
    logger.info("Calculating technical indicators...")
    df = pipeline.calculate_features(df)
    
    # Detect market regimes
    logger.info("Detecting market regimes...")
    regime_detector = MarketRegimeDetector()
    df = regime_detector.calculate_regime_features(df)
    df = regime_detector.detect_regimes(df)
    
    # Generate simple signals based on RSI and regime
    signals = (
        ((df['rsi_14'] < 30) & (df['regime'] == 0)).astype(int) -
        ((df['rsi_14'] > 70) & (df['regime'] == 3)).astype(int)
    )
    
    logger.info(f"Generated {(signals != 0).sum()} signals")
    
    # Run backtest
    logger.info("\n=== Running Backtest ===")
    engine = BacktestEngine(
        initial_capital=10000.0,
        commission=0.0006,
        slippage=0.0001,
        leverage=1
    )
    
    results = engine.run_backtest(df, signals)
    
    # Print results
    logger.info("\n=== Backtest Results ===")
    logger.info(f"Initial Capital: ${results['initial_capital']:.2f}")
    logger.info(f"Final Capital: ${results['final_capital']:.2f}")
    logger.info(f"Total Return: {results['total_return']*100:.2f}%")
    logger.info(f"Total Trades: {results['total_trades']}")
    logger.info(f"Win Rate: {results['win_rate']*100:.2f}%")
    logger.info(f"Profit Factor: {results['profit_factor']:.2f}")
    logger.info(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
    logger.info(f"Max Drawdown: {results['max_drawdown']*100:.2f}%")
    
    # Get trade analysis
    trades_df = engine.get_trade_analysis()
    logger.info(f"\nFirst 5 trades:\n{trades_df.head()}")
    
    await exchange.disconnect()


if __name__ == '__main__':
    asyncio.run(run_backtest())

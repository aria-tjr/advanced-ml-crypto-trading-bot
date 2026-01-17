"""
Example: Live Trading Bot
Demonstrates how to run the bot in live mode
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from bot.main import TradingBot
from loguru import logger


async def run_live_bot():
    """Run bot in live mode"""
    
    logger.info("Starting live trading bot...")
    logger.warning("Make sure you have configured API keys in .env file!")
    
    # Initialize bot
    bot = TradingBot(config_path='config/config.yaml')
    
    try:
        # Initialize connections
        await bot.initialize()
        
        # Train models (optional - can load pre-trained models)
        for symbol in bot.config.trading.symbols:
            logger.info(f"Training models for {symbol}...")
            await bot.train_models(symbol)
        
        # Run trading strategy
        await bot.run_strategy()
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await bot.shutdown()


if __name__ == '__main__':
    asyncio.run(run_live_bot())

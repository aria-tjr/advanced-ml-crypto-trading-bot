#!/usr/bin/env python3
"""
Quick Start Script
Simplified interface to get started with the trading bot
"""

import asyncio
import sys
from pathlib import Path
import argparse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from bot.main import TradingBot
from bot.config import load_config
from loguru import logger


def print_banner():
    """Print welcome banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   Advanced ML Crypto Futures Trading Bot                 ║
    ║   Professional Automated Trading System                   ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_menu():
    """Print main menu"""
    print("\n" + "="*60)
    print("MAIN MENU")
    print("="*60)
    print("1. Run Backtest")
    print("2. Train ML Models")
    print("3. Start Paper Trading (Testnet)")
    print("4. Start Live Trading (Real Money)")
    print("5. View Configuration")
    print("6. Check Account Balance")
    print("7. Exit")
    print("="*60)


async def run_backtest(bot: TradingBot):
    """Run backtest mode"""
    print("\n📊 Running Backtest...")
    print("="*60)
    
    config = bot.config
    
    # Get parameters from user
    symbol = input(f"Symbol (default: {config.trading.symbols[0]}): ") or config.trading.symbols[0]
    start_date = input("Start date (YYYY-MM-DD, default: 2023-01-01): ") or "2023-01-01"
    end_date = input("End date (YYYY-MM-DD, default: 2023-12-31): ") or "2023-12-31"
    
    try:
        results = await bot.run_backtest(symbol, start_date, end_date)
        
        print("\n" + "="*60)
        print("BACKTEST RESULTS")
        print("="*60)
        print(f"Initial Capital:  ${results['initial_capital']:,.2f}")
        print(f"Final Capital:    ${results['final_capital']:,.2f}")
        print(f"Total Return:     {results['total_return']*100:.2f}%")
        print(f"Total Trades:     {results['total_trades']}")
        print(f"Win Rate:         {results['win_rate']*100:.2f}%")
        print(f"Profit Factor:    {results['profit_factor']:.2f}")
        print(f"Sharpe Ratio:     {results['sharpe_ratio']:.2f}")
        print(f"Sortino Ratio:    {results['sortino_ratio']:.2f}")
        print(f"Max Drawdown:     {results['max_drawdown']*100:.2f}%")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Backtest failed: {e}")


async def train_models(bot: TradingBot):
    """Train ML models"""
    print("\n🧠 Training ML Models...")
    print("="*60)
    
    for symbol in bot.config.trading.symbols:
        print(f"\nTraining models for {symbol}...")
        try:
            await bot.train_models(symbol)
            print(f"✅ {symbol} models trained successfully")
        except Exception as e:
            logger.error(f"Failed to train {symbol}: {e}")
    
    print("\n✅ Model training complete!")


async def start_paper_trading(bot: TradingBot):
    """Start paper trading"""
    print("\n📄 Starting Paper Trading (Testnet)...")
    print("="*60)
    
    if not bot.config.exchange.testnet:
        print("⚠️  WARNING: Testnet is not enabled in config!")
        confirm = input("Continue anyway? (yes/no): ")
        if confirm.lower() != 'yes':
            return
    
    print("Starting bot in paper trading mode...")
    print("Press Ctrl+C to stop")
    
    try:
        await bot.run_strategy()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping paper trading...")


async def start_live_trading(bot: TradingBot):
    """Start live trading"""
    print("\n💰 Starting Live Trading (REAL MONEY)...")
    print("="*60)
    
    if bot.config.exchange.testnet:
        print("⚠️  Testnet is enabled. Disable it for live trading.")
        return
    
    # Safety confirmations
    print("\n⚠️  WARNING: This will trade with REAL MONEY!")
    print("Please confirm the following:")
    print(f"1. Exchange: {bot.config.exchange.name}")
    print(f"2. Symbols: {', '.join(bot.config.trading.symbols)}")
    print(f"3. Max Position Size: {bot.config.risk.max_position_size*100}%")
    print(f"4. Leverage: {bot.config.trading.leverage}x")
    
    confirm1 = input("\nType 'I UNDERSTAND THE RISKS' to continue: ")
    if confirm1 != 'I UNDERSTAND THE RISKS':
        print("Cancelled.")
        return
    
    confirm2 = input("Type 'START LIVE TRADING' to confirm: ")
    if confirm2 != 'START LIVE TRADING':
        print("Cancelled.")
        return
    
    print("\n🚀 Starting live trading...")
    print("Monitor closely! Press Ctrl+C to stop")
    
    try:
        await bot.run_strategy()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping live trading...")


async def view_configuration(bot: TradingBot):
    """View current configuration"""
    print("\n⚙️  Current Configuration")
    print("="*60)
    
    config = bot.config
    
    print(f"\nExchange:")
    print(f"  Name:     {config.exchange.name}")
    print(f"  Testnet:  {config.exchange.testnet}")
    
    print(f"\nTrading:")
    print(f"  Symbols:       {', '.join(config.trading.symbols)}")
    print(f"  Timeframe:     {config.trading.timeframe}")
    print(f"  Max Positions: {config.trading.max_positions}")
    print(f"  Leverage:      {config.trading.leverage}x")
    
    print(f"\nRisk Management:")
    print(f"  Max Position:  {config.risk.max_position_size*100}%")
    print(f"  Stop Loss:     {config.risk.stop_loss_pct*100}%")
    print(f"  Take Profit:   {config.risk.take_profit_pct*100}%")
    print(f"  Max Daily Loss: {config.risk.max_daily_loss*100}%")
    
    print(f"\nML Models:")
    print(f"  Type:              {config.ml.model_type}")
    print(f"  Lookback Period:   {config.ml.lookback_period}")
    print(f"  Retrain Interval:  {config.ml.retrain_interval}h")


async def check_balance(bot: TradingBot):
    """Check account balance"""
    print("\n💵 Checking Account Balance...")
    print("="*60)
    
    try:
        balance = await bot.exchange.get_balance()
        
        print("\nAccount Balances:")
        for asset, amounts in balance.items():
            print(f"\n{asset}:")
            print(f"  Free:  {amounts['free']:,.8f}")
            print(f"  Used:  {amounts['used']:,.8f}")
            print(f"  Total: {amounts['total']:,.8f}")
        
        # Check positions
        positions = await bot.exchange.get_positions()
        
        if positions:
            print("\n📈 Open Positions:")
            for pos in positions:
                print(f"\n{pos['symbol']}:")
                print(f"  Side:       {pos['side']}")
                print(f"  Size:       {pos['size']}")
                print(f"  Entry:      {pos['entry_price']}")
                print(f"  Unrealized: {pos['unrealized_pnl']:.2f}")
        else:
            print("\n📭 No open positions")
            
    except Exception as e:
        logger.error(f"Failed to get balance: {e}")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Trading Bot Quick Start')
    parser.add_argument('--config', type=str, default='config/config.yaml',
                      help='Path to configuration file')
    args = parser.parse_args()
    
    print_banner()
    
    # Initialize bot
    print("Initializing bot...")
    bot = TradingBot(config_path=args.config)
    await bot.initialize()
    
    # Main loop
    while True:
        print_menu()
        choice = input("\nEnter your choice (1-7): ")
        
        if choice == '1':
            await run_backtest(bot)
        elif choice == '2':
            await train_models(bot)
        elif choice == '3':
            await start_paper_trading(bot)
        elif choice == '4':
            await start_live_trading(bot)
        elif choice == '5':
            await view_configuration(bot)
        elif choice == '6':
            await check_balance(bot)
        elif choice == '7':
            print("\n👋 Goodbye!")
            await bot.shutdown()
            break
        else:
            print("❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

"""
Backtesting Engine
Vectorized backtesting framework for strategy evaluation
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Callable
from datetime import datetime
from loguru import logger


class BacktestEngine:
    """Backtesting engine for trading strategies"""
    
    def __init__(self, initial_capital: float = 10000.0, commission: float = 0.0006,
                 slippage: float = 0.0001, leverage: int = 1):
        """
        Initialize backtest engine
        
        Args:
            initial_capital: Starting capital
            commission: Trading commission rate
            slippage: Slippage rate
            leverage: Leverage multiplier
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.leverage = leverage
        
        self.trades = []
        self.equity_curve = []
        self.positions = []
    
    def run_backtest(self, data: pd.DataFrame, signals: pd.Series,
                    position_size_func: Optional[Callable] = None) -> Dict:
        """
        Run backtest on historical data
        
        Args:
            data: DataFrame with OHLCV data
            signals: Series with trading signals (1: long, -1: short, 0: neutral)
            position_size_func: Optional function to calculate position size
            
        Returns:
            Dictionary with backtest results
        """
        logger.info(f"Running backtest on {len(data)} periods")
        
        # Initialize
        capital = self.initial_capital
        position = 0
        position_price = 0
        equity = [capital]
        trades = []
        
        for i in range(1, len(data)):
            current_price = data['close'].iloc[i]
            signal = signals.iloc[i]
            prev_signal = signals.iloc[i - 1]
            
            # Check for position entry/exit
            if signal != prev_signal:
                # Close existing position
                if position != 0:
                    pnl = self._calculate_pnl(position, position_price, current_price)
                    capital += pnl
                    
                    trades.append({
                        'entry_time': data.index[i - 1],
                        'exit_time': data.index[i],
                        'entry_price': position_price,
                        'exit_price': current_price,
                        'side': 'LONG' if position > 0 else 'SHORT',
                        'pnl': pnl,
                        'pnl_pct': pnl / (position_price * abs(position))
                    })
                    
                    position = 0
                
                # Open new position
                if signal != 0:
                    if position_size_func:
                        position_size = position_size_func(capital, current_price)
                    else:
                        position_size = capital * 0.1  # Default 10% of capital
                    
                    position = signal * (position_size / current_price)
                    position_price = current_price * (1 + signal * self.slippage)
                    
                    # Apply commission
                    capital -= abs(position * position_price) * self.commission
            
            # Calculate current equity
            if position != 0:
                unrealized_pnl = self._calculate_pnl(position, position_price, current_price)
                current_equity = capital + unrealized_pnl
            else:
                current_equity = capital
            
            equity.append(current_equity)
        
        # Close any remaining position
        if position != 0:
            pnl = self._calculate_pnl(position, position_price, data['close'].iloc[-1])
            capital += pnl
            
            trades.append({
                'entry_time': data.index[-2],
                'exit_time': data.index[-1],
                'entry_price': position_price,
                'exit_price': data['close'].iloc[-1],
                'side': 'LONG' if position > 0 else 'SHORT',
                'pnl': pnl,
                'pnl_pct': pnl / (position_price * abs(position))
            })
        
        self.trades = trades
        self.equity_curve = equity
        
        # Calculate metrics
        results = self._calculate_metrics(pd.DataFrame(trades), pd.Series(equity))
        
        logger.info(f"Backtest complete. Final capital: ${results['final_capital']:.2f}")
        
        return results
    
    def _calculate_pnl(self, position: float, entry_price: float, exit_price: float) -> float:
        """Calculate P&L for a position"""
        if position > 0:  # Long
            gross_pnl = position * (exit_price - entry_price)
        else:  # Short
            gross_pnl = position * (exit_price - entry_price)
        
        # Apply commission
        commission_cost = abs(position * exit_price) * self.commission
        net_pnl = gross_pnl - commission_cost
        
        return net_pnl
    
    def _calculate_metrics(self, trades_df: pd.DataFrame, equity: pd.Series) -> Dict:
        """Calculate performance metrics"""
        if len(trades_df) == 0:
            return {'error': 'No trades executed'}
        
        # Basic metrics
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['pnl'] > 0])
        losing_trades = len(trades_df[trades_df['pnl'] < 0])
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        total_pnl = trades_df['pnl'].sum()
        avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
        
        # Risk metrics
        returns = equity.pct_change().dropna()
        
        sharpe_ratio = self._calculate_sharpe(returns)
        sortino_ratio = self._calculate_sortino(returns)
        max_drawdown, max_dd_duration = self._calculate_max_drawdown(equity)
        
        # Profit factor
        gross_profit = trades_df[trades_df['pnl'] > 0]['pnl'].sum()
        gross_loss = abs(trades_df[trades_df['pnl'] < 0]['pnl'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        return {
            'initial_capital': self.initial_capital,
            'final_capital': equity.iloc[-1],
            'total_return': (equity.iloc[-1] - self.initial_capital) / self.initial_capital,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'max_drawdown_duration': max_dd_duration,
            'total_pnl': total_pnl
        }
    
    def _calculate_sharpe(self, returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """Calculate Sharpe ratio"""
        excess_returns = returns - risk_free_rate
        if excess_returns.std() == 0:
            return 0.0
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()
    
    def _calculate_sortino(self, returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """Calculate Sortino ratio"""
        excess_returns = returns - risk_free_rate
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0
        
        return np.sqrt(252) * excess_returns.mean() / downside_returns.std()
    
    def _calculate_max_drawdown(self, equity: pd.Series) -> tuple:
        """Calculate maximum drawdown and duration"""
        running_max = equity.expanding().max()
        drawdown = (equity - running_max) / running_max
        
        max_dd = drawdown.min()
        
        # Calculate duration
        in_drawdown = False
        current_duration = 0
        max_duration = 0
        
        for dd in drawdown:
            if dd < 0:
                if not in_drawdown:
                    in_drawdown = True
                    current_duration = 1
                else:
                    current_duration += 1
                    max_duration = max(max_duration, current_duration)
            else:
                in_drawdown = False
                current_duration = 0
        
        return max_dd, max_duration
    
    def get_trade_analysis(self) -> pd.DataFrame:
        """Get detailed trade analysis"""
        if not self.trades:
            return pd.DataFrame()
        
        return pd.DataFrame(self.trades)
    
    def get_equity_curve(self) -> pd.Series:
        """Get equity curve"""
        return pd.Series(self.equity_curve)
    
    def walk_forward_analysis(self, data: pd.DataFrame, signals_func: Callable,
                            train_window: int = 252, test_window: int = 63) -> Dict:
        """
        Perform walk-forward analysis
        
        Args:
            data: Historical data
            signals_func: Function to generate signals
            train_window: Training window size
            test_window: Testing window size
            
        Returns:
            Dictionary with walk-forward results
        """
        logger.info("Running walk-forward analysis")
        
        results = []
        n_periods = len(data)
        current_pos = train_window
        
        while current_pos + test_window <= n_periods:
            # Train on window
            train_data = data.iloc[current_pos - train_window:current_pos]
            
            # Generate signals for test window
            test_data = data.iloc[current_pos:current_pos + test_window]
            signals = signals_func(test_data)
            
            # Run backtest on test window
            test_results = self.run_backtest(test_data, signals)
            results.append(test_results)
            
            current_pos += test_window
        
        # Aggregate results
        avg_return = np.mean([r['total_return'] for r in results])
        avg_sharpe = np.mean([r['sharpe_ratio'] for r in results])
        avg_max_dd = np.mean([r['max_drawdown'] for r in results])
        
        return {
            'n_periods': len(results),
            'avg_return': avg_return,
            'avg_sharpe': avg_sharpe,
            'avg_max_drawdown': avg_max_dd,
            'all_results': results
        }

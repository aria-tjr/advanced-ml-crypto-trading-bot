"""
Risk Management Module
Position sizing, stop loss, take profit, and portfolio risk management
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple
from loguru import logger


class RiskManager:
    """Risk management and position sizing"""
    
    def __init__(self, max_position_size: float = 0.1, stop_loss_pct: float = 0.02,
                 take_profit_pct: float = 0.04, max_daily_loss: float = 0.05,
                 risk_per_trade: float = 0.01, use_kelly: bool = True):
        """
        Initialize risk manager
        
        Args:
            max_position_size: Maximum position size as fraction of portfolio
            stop_loss_pct: Stop loss percentage
            take_profit_pct: Take profit percentage
            max_daily_loss: Maximum daily loss as fraction of portfolio
            risk_per_trade: Risk per trade as fraction of portfolio
            use_kelly: Use Kelly criterion for position sizing
        """
        self.max_position_size = max_position_size
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.max_daily_loss = max_daily_loss
        self.risk_per_trade = risk_per_trade
        self.use_kelly = use_kelly
        
        self.daily_pnl = 0.0
        self.trades_today = []
    
    def calculate_position_size(self, account_balance: float, entry_price: float,
                                stop_loss_price: float, win_rate: Optional[float] = None,
                                avg_win: Optional[float] = None, 
                                avg_loss: Optional[float] = None) -> float:
        """
        Calculate optimal position size
        
        Args:
            account_balance: Current account balance
            entry_price: Entry price
            stop_loss_price: Stop loss price
            win_rate: Historical win rate (for Kelly criterion)
            avg_win: Average win amount
            avg_loss: Average loss amount
            
        Returns:
            Position size in base currency
        """
        # Fixed fractional position sizing
        risk_amount = account_balance * self.risk_per_trade
        price_risk = abs(entry_price - stop_loss_price) / entry_price
        
        if price_risk == 0:
            logger.warning("Price risk is zero, using default position size")
            position_size = account_balance * 0.01
        else:
            position_size = risk_amount / price_risk
        
        # Apply Kelly criterion if enabled and stats available
        if self.use_kelly and win_rate and avg_win and avg_loss:
            kelly_fraction = self.calculate_kelly_criterion(win_rate, avg_win, avg_loss)
            kelly_position = account_balance * kelly_fraction
            position_size = min(position_size, kelly_position)
        
        # Apply maximum position size constraint
        max_position = account_balance * self.max_position_size
        position_size = min(position_size, max_position)
        
        return position_size
    
    def calculate_kelly_criterion(self, win_rate: float, avg_win: float, 
                                  avg_loss: float) -> float:
        """
        Calculate Kelly criterion for optimal position sizing
        
        Args:
            win_rate: Probability of winning
            avg_win: Average win amount
            avg_loss: Average loss amount
            
        Returns:
            Kelly fraction
        """
        if avg_loss == 0:
            return 0.0
        
        win_loss_ratio = avg_win / avg_loss
        kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        
        # Use half-Kelly for safety
        kelly = max(0, kelly) * 0.5
        
        # Cap at maximum position size
        return min(kelly, self.max_position_size)
    
    def calculate_stop_loss(self, entry_price: float, side: str, 
                           volatility: Optional[float] = None) -> float:
        """
        Calculate stop loss price
        
        Args:
            entry_price: Entry price
            side: 'BUY' or 'SELL'
            volatility: Current volatility (ATR)
            
        Returns:
            Stop loss price
        """
        # Use volatility-based stop if available
        if volatility:
            stop_distance = max(volatility * 2, entry_price * self.stop_loss_pct)
        else:
            stop_distance = entry_price * self.stop_loss_pct
        
        if side.upper() == 'BUY':
            return entry_price - stop_distance
        else:
            return entry_price + stop_distance
    
    def calculate_take_profit(self, entry_price: float, side: str,
                             risk_reward_ratio: float = 2.0) -> float:
        """
        Calculate take profit price
        
        Args:
            entry_price: Entry price
            side: 'BUY' or 'SELL'
            risk_reward_ratio: Reward to risk ratio
            
        Returns:
            Take profit price
        """
        profit_distance = entry_price * self.take_profit_pct * risk_reward_ratio
        
        if side.upper() == 'BUY':
            return entry_price + profit_distance
        else:
            return entry_price - profit_distance
    
    def check_daily_loss_limit(self, current_pnl: float, account_balance: float) -> bool:
        """
        Check if daily loss limit is reached
        
        Args:
            current_pnl: Current daily P&L
            account_balance: Account balance
            
        Returns:
            True if trading should continue, False if limit reached
        """
        self.daily_pnl = current_pnl
        max_loss = account_balance * self.max_daily_loss
        
        if self.daily_pnl < -max_loss:
            logger.warning(f"Daily loss limit reached: {self.daily_pnl:.2f}")
            return False
        
        return True
    
    def calculate_leverage(self, position_size: float, account_balance: float,
                          max_leverage: int = 10) -> int:
        """
        Calculate optimal leverage
        
        Args:
            position_size: Desired position size
            account_balance: Available balance
            max_leverage: Maximum allowed leverage
            
        Returns:
            Leverage to use
        """
        required_leverage = position_size / account_balance
        leverage = min(int(np.ceil(required_leverage)), max_leverage)
        
        return max(1, leverage)
    
    def adjust_position_for_correlation(self, base_size: float, correlations: Dict[str, float],
                                       existing_positions: Dict[str, float]) -> float:
        """
        Adjust position size based on portfolio correlation
        
        Args:
            base_size: Base position size
            correlations: Correlation with existing positions
            existing_positions: Current position sizes
            
        Returns:
            Adjusted position size
        """
        if not existing_positions:
            return base_size
        
        # Calculate correlation penalty
        total_correlation = sum(correlations.get(symbol, 0) * size 
                               for symbol, size in existing_positions.items())
        
        # Reduce size if highly correlated
        correlation_factor = 1 - abs(total_correlation) * 0.3
        adjusted_size = base_size * max(0.5, correlation_factor)
        
        return adjusted_size
    
    def calculate_var(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """
        Calculate Value at Risk (VaR)
        
        Args:
            returns: Historical returns
            confidence_level: Confidence level for VaR
            
        Returns:
            VaR value
        """
        var = np.percentile(returns, (1 - confidence_level) * 100)
        return abs(var)
    
    def calculate_cvar(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """
        Calculate Conditional Value at Risk (CVaR/Expected Shortfall)
        
        Args:
            returns: Historical returns
            confidence_level: Confidence level
            
        Returns:
            CVaR value
        """
        var = self.calculate_var(returns, confidence_level)
        cvar = returns[returns <= -var].mean()
        return abs(cvar)
    
    def calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """
        Calculate Sharpe ratio
        
        Args:
            returns: Returns series
            risk_free_rate: Risk-free rate
            
        Returns:
            Sharpe ratio
        """
        excess_returns = returns - risk_free_rate
        if excess_returns.std() == 0:
            return 0.0
        
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()
    
    def calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """
        Calculate Sortino ratio (downside risk)
        
        Args:
            returns: Returns series
            risk_free_rate: Risk-free rate
            
        Returns:
            Sortino ratio
        """
        excess_returns = returns - risk_free_rate
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0
        
        return np.sqrt(252) * excess_returns.mean() / downside_returns.std()
    
    def calculate_max_drawdown(self, equity_curve: pd.Series) -> Tuple[float, int]:
        """
        Calculate maximum drawdown
        
        Args:
            equity_curve: Equity curve series
            
        Returns:
            Tuple of (max_drawdown, duration_days)
        """
        cumulative = equity_curve
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        max_dd = drawdown.min()
        
        # Calculate duration
        dd_duration = 0
        current_dd_duration = 0
        is_in_drawdown = False
        
        for dd in drawdown:
            if dd < 0:
                if not is_in_drawdown:
                    is_in_drawdown = True
                    current_dd_duration = 1
                else:
                    current_dd_duration += 1
            else:
                if is_in_drawdown:
                    max_dd_duration = max(dd_duration, current_dd_duration)
                    dd_duration = max_dd_duration
                    is_in_drawdown = False
                    current_dd_duration = 0
        
        return max_dd, dd_duration
    
    def should_take_trade(self, signal_strength: float, regime: str,
                         account_balance: float, open_positions: int) -> bool:
        """
        Determine if trade should be taken based on risk checks
        
        Args:
            signal_strength: Signal strength (0-1)
            regime: Current market regime
            account_balance: Current balance
            open_positions: Number of open positions
            
        Returns:
            True if trade should be taken
        """
        # Check daily loss limit
        if not self.check_daily_loss_limit(self.daily_pnl, account_balance):
            return False
        
        # Check signal strength
        if signal_strength < 0.6:
            return False
        
        # Check if too many positions
        max_positions = int(1 / self.max_position_size)
        if open_positions >= max_positions:
            return False
        
        # Regime-based filter (example: avoid high volatility bearish)
        if regime == 'high_volatility_bearish' and signal_strength < 0.8:
            return False
        
        return True

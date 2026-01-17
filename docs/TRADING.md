# Trading Guide

## Getting Started with Live Trading

### ⚠️ IMPORTANT: Start with Testnet

Before risking real funds, always:
1. Test on exchange testnet
2. Run backtests on historical data
3. Paper trade for at least 1 month
4. Start with small position sizes

## Step-by-Step Guide

### 1. Setup API Keys

#### Binance
1. Go to [Binance API Management](https://www.binance.com/en/my/settings/api-management)
2. Create new API key
3. Enable "Enable Futures"
4. Whitelist your IP (recommended)
5. Save API key and secret

#### Bybit
1. Go to [Bybit API Management](https://www.bybit.com/app/user/api-management)
2. Create new API key
3. Enable "Contract Trading"
4. Whitelist your IP
5. Save API key and secret

### 2. Configure Bot

Edit `config/config.yaml`:

```yaml
exchange:
  name: binance
  testnet: true  # Start here!

trading:
  symbols:
    - BTCUSDT     # Start with liquid pairs
  timeframe: 1h   # Longer timeframes = more stable
  max_positions: 3
  leverage: 5     # Use low leverage initially
```

### 3. Train Models

```bash
python examples/train_models.py
```

Monitor training metrics:
- Validation loss should decrease
- R² score > 0.5 is good
- Check feature importance

### 4. Run Backtest

```bash
python examples/run_backtest.py
```

Acceptable metrics:
- ✅ Sharpe Ratio > 1.0
- ✅ Win Rate > 50%
- ✅ Profit Factor > 1.5
- ✅ Max Drawdown < 20%

### 5. Paper Trading (Testnet)

```bash
# Make sure testnet is enabled
python examples/live_trading.py
```

Run for at least 2 weeks and monitor:
- Order execution
- P&L tracking
- Risk management
- Error handling

### 6. Go Live (Real Trading)

Only after successful paper trading:

```yaml
exchange:
  testnet: false  # Enable live trading
```

Start with:
- Small capital (1-5% of trading capital)
- Low leverage (1-3x)
- Conservative position sizing
- Close monitoring

## Trading Strategies

### Conservative Strategy

```yaml
risk:
  max_position_size: 0.05   # 5% per trade
  stop_loss_pct: 0.015      # 1.5%
  take_profit_pct: 0.03     # 3%
  risk_per_trade: 0.005     # 0.5%

trading:
  leverage: 2
  max_positions: 2
```

**Expected:**
- Lower returns (10-30% annually)
- Lower risk (max DD < 10%)
- Fewer trades
- More stable

### Moderate Strategy

```yaml
risk:
  max_position_size: 0.1    # 10% per trade
  stop_loss_pct: 0.02       # 2%
  take_profit_pct: 0.04     # 4%
  risk_per_trade: 0.01      # 1%

trading:
  leverage: 5
  max_positions: 3
```

**Expected:**
- Medium returns (30-60% annually)
- Medium risk (max DD 10-20%)
- Moderate trade frequency
- Balanced approach

### Aggressive Strategy

```yaml
risk:
  max_position_size: 0.2    # 20% per trade
  stop_loss_pct: 0.03       # 3%
  take_profit_pct: 0.06     # 6%
  risk_per_trade: 0.02      # 2%

trading:
  leverage: 10
  max_positions: 5
```

**Expected:**
- Higher returns (60-100%+ annually)
- Higher risk (max DD 20-40%)
- More trades
- Requires close monitoring

## Monitoring

### Daily Checks

- [ ] Check open positions
- [ ] Review P&L
- [ ] Check for errors in logs
- [ ] Verify account balance
- [ ] Review recent trades

### Weekly Tasks

- [ ] Analyze performance metrics
- [ ] Review risk metrics
- [ ] Check model predictions
- [ ] Update risk parameters if needed
- [ ] Backup trading data

### Monthly Tasks

- [ ] Retrain models
- [ ] Comprehensive performance review
- [ ] Strategy optimization
- [ ] Risk assessment
- [ ] Portfolio rebalancing

## Common Issues

### Low Win Rate

**Solutions:**
- Increase signal threshold
- Add more filters
- Improve feature engineering
- Use longer timeframes

### High Drawdown

**Solutions:**
- Reduce position sizes
- Tighten stop losses
- Reduce leverage
- Add more diversification

### Frequent False Signals

**Solutions:**
- Use ensemble models
- Add regime detection
- Filter by volatility
- Require stronger signals

### Slippage Too High

**Solutions:**
- Use limit orders instead of market
- Trade more liquid pairs
- Avoid volatile periods
- Reduce position sizes

## Risk Management Rules

### Position Sizing

```python
# Never risk more than 1-2% per trade
max_risk = account_balance * 0.01

# Position size based on stop loss
position_size = max_risk / stop_loss_distance
```

### Stop Loss

```python
# Always use stop losses
# Minimum 1.5%, adjust based on volatility
stop_loss = entry_price * (1 - 0.015)
```

### Take Profit

```python
# Minimum 2:1 reward-to-risk ratio
take_profit = entry_price * (1 + 0.03)
```

### Daily Loss Limit

```python
# Stop trading if daily loss exceeds 5%
if daily_pnl < -account_balance * 0.05:
    stop_trading_for_today()
```

## Performance Tracking

### Key Metrics

```python
# Sharpe Ratio
sharpe = (returns.mean() - rf_rate) / returns.std() * sqrt(252)

# Maximum Drawdown
max_dd = (equity - equity.cummax()) / equity.cummax()

# Win Rate
win_rate = winning_trades / total_trades

# Profit Factor
profit_factor = gross_profit / abs(gross_loss)
```

### Targets

- Sharpe Ratio: > 1.5
- Max Drawdown: < 20%
- Win Rate: > 50%
- Profit Factor: > 2.0

## Emergency Procedures

### System Failure

1. Manually close all positions
2. Cancel all pending orders
3. Disable API keys
4. Check account balance
5. Review logs
6. Fix issues before restarting

### Rapid Drawdown

1. Stop bot immediately
2. Close losing positions
3. Reduce position sizes
4. Review strategy
5. Re-backtest before resuming

### API Issues

1. Switch to backup exchange
2. Use manual trading
3. Contact exchange support
4. Check API permissions
5. Rotate API keys

## Advanced Tips

### Optimization

- Use walk-forward analysis
- Optimize for Sharpe, not returns
- Test on out-of-sample data
- Consider transaction costs
- Account for slippage

### Diversification

- Trade multiple pairs
- Use different timeframes
- Combine strategies
- Balance long/short
- Diversify across exchanges

### Automation

- Set up monitoring alerts
- Automate daily reports
- Use webhooks for notifications
- Backup data regularly
- Log all activities

## Legal & Tax

- Understand crypto regulations in your country
- Keep detailed trading records
- Report gains/losses to tax authorities
- Consider consulting a tax professional
- Maintain compliance with local laws

## Support

If you encounter issues:

1. Check logs in `logs/` directory
2. Review [Documentation](../README.md)
3. Search [GitHub Issues](https://github.com/aria-tjr/advanced-ml-crypto-trading-bot/issues)
4. Open new issue with details
5. Join community discussions

## Remember

> "Risk management is more important than prediction accuracy."

- Never trade with money you can't afford to lose
- Always use stop losses
- Start small and scale gradually
- Monitor performance regularly
- Adjust strategy based on results
- Stay disciplined and patient

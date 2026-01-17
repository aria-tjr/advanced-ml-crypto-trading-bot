# Configuration Guide

## Overview

The bot uses a combination of YAML configuration files and environment variables for settings.

## Configuration Files

### Main Configuration: `config/config.yaml`

```yaml
# Exchange settings
exchange:
  name: binance              # binance, bybit, kucoin
  testnet: true              # Always start with testnet!
  rate_limit: 1200           # Requests per minute

# Trading parameters
trading:
  symbols:
    - BTCUSDT
    - ETHUSDT
    - BNBUSDT
  timeframe: 1h              # 1m, 5m, 15m, 1h, 4h, 1d
  max_positions: 5           # Maximum concurrent positions
  leverage: 10               # Leverage multiplier (1-125)
  order_type: LIMIT          # LIMIT or MARKET

# Risk management
risk:
  max_position_size: 0.1     # 10% of portfolio per position
  stop_loss_pct: 0.02        # 2% stop loss
  take_profit_pct: 0.04      # 4% take profit (2:1 R:R)
  max_daily_loss: 0.05       # 5% maximum daily loss
  risk_per_trade: 0.01       # 1% risk per trade
  use_kelly_criterion: true  # Use Kelly criterion for sizing

# ML models
ml:
  model_type: ensemble       # xgboost, lstm, transformer, ensemble
  retrain_interval: 24       # Retrain every N hours
  lookback_period: 100       # Historical periods for features
  prediction_horizon: 1      # Predict N periods ahead
  feature_count: 200         # Number of features to use

# Backtesting
backtest:
  start_date: "2023-01-01"
  end_date: "2023-12-31"
  initial_capital: 10000.0
  commission: 0.0006         # 0.06% per trade
  slippage: 0.0001           # 0.01% slippage

# Paths
data_dir: data
models_dir: models
logs_dir: logs
```

### Environment Variables: `.env`

```bash
# Environment
ENVIRONMENT=development      # development, staging, production

# Exchange API Keys
EXCHANGE_NAME=binance
EXCHANGE_API_KEY=your_api_key_here
EXCHANGE_API_SECRET=your_api_secret_here
EXCHANGE_TESTNET=true

# Trading Symbols (comma-separated)
TRADING_SYMBOLS=BTCUSDT,ETHUSDT

# Risk Settings
RISK_MAX_POSITION_SIZE=0.1
RISK_STOP_LOSS_PCT=0.02
RISK_TAKE_PROFIT_PCT=0.04

# ML Settings
ML_MODEL_TYPE=ensemble
ML_LOOKBACK_PERIOD=100
```

## Exchange-Specific Configuration

### Binance

```python
exchange = BinanceExchange(
    api_key="your_api_key",
    api_secret="your_api_secret",
    testnet=True  # Use testnet first!
)
```

**API Permissions Required:**
- ✅ Enable Reading
- ✅ Enable Futures
- ✅ Enable Spot & Margin Trading
- ❌ Enable Withdrawals (not needed)

### Bybit

```python
exchange = BybitExchange(
    api_key="your_api_key",
    api_secret="your_api_secret",
    testnet=True
)
```

**API Permissions Required:**
- ✅ Contract Trade
- ✅ Contract Read
- ❌ Withdrawal (not needed)

### KuCoin

```python
exchange = KuCoinExchange(
    api_key="your_api_key",
    api_secret="your_api_secret",
    passphrase="your_passphrase",
    testnet=True
)
```

**API Permissions Required:**
- ✅ General
- ✅ Trade
- ❌ Transfer (not needed)
- ❌ Withdraw (not needed)

## Risk Configuration

### Conservative (Low Risk)

```yaml
risk:
  max_position_size: 0.05    # 5% per position
  stop_loss_pct: 0.015       # 1.5% stop loss
  take_profit_pct: 0.03      # 3% take profit
  max_daily_loss: 0.03       # 3% max daily loss
  risk_per_trade: 0.005      # 0.5% risk per trade
```

### Moderate (Medium Risk)

```yaml
risk:
  max_position_size: 0.1     # 10% per position
  stop_loss_pct: 0.02        # 2% stop loss
  take_profit_pct: 0.04      # 4% take profit
  max_daily_loss: 0.05       # 5% max daily loss
  risk_per_trade: 0.01       # 1% risk per trade
```

### Aggressive (High Risk)

```yaml
risk:
  max_position_size: 0.2     # 20% per position
  stop_loss_pct: 0.03        # 3% stop loss
  take_profit_pct: 0.06      # 6% take profit
  max_daily_loss: 0.10       # 10% max daily loss
  risk_per_trade: 0.02       # 2% risk per trade
```

## ML Model Configuration

### XGBoost Only

```yaml
ml:
  model_type: xgboost
  lookback_period: 100
  prediction_horizon: 1
```

### LSTM Only

```yaml
ml:
  model_type: lstm
  lookback_period: 100
  prediction_horizon: 1
  hidden_size: 128
  num_layers: 2
```

### Transformer Only

```yaml
ml:
  model_type: transformer
  lookback_period: 100
  prediction_horizon: 1
  d_model: 128
  nhead: 8
  num_encoder_layers: 3
```

### Ensemble (Recommended)

```yaml
ml:
  model_type: ensemble
  lookback_period: 100
  prediction_horizon: 1
```

## Timeframe Configuration

Supported timeframes:
- `1m` - 1 minute
- `5m` - 5 minutes
- `15m` - 15 minutes
- `1h` - 1 hour (recommended)
- `4h` - 4 hours
- `1d` - 1 day

**Recommendation**: Start with `1h` or `4h` for more stable signals.

## Symbol Configuration

### Single Symbol

```yaml
trading:
  symbols:
    - BTCUSDT
```

### Multiple Symbols

```yaml
trading:
  symbols:
    - BTCUSDT
    - ETHUSDT
    - BNBUSDT
    - ADAUSDT
    - SOLUSDT
```

**Note**: More symbols = more capital required to diversify positions.

## Security Best Practices

1. **Never commit API keys to Git**
   - Add `.env` to `.gitignore`
   - Use environment variables

2. **Use API restrictions**
   - Whitelist your IP address
   - Disable withdrawals
   - Use testnet first

3. **Rotate API keys regularly**
   - Change keys every 30-90 days
   - Use separate keys for testing

4. **Monitor bot activity**
   - Check logs regularly
   - Set up alerts for unusual activity

## Validation

Validate your configuration:

```bash
python -c "from bot.config import load_config; c = load_config('config/config.yaml'); print('Config valid!')"
```

## Examples

See `examples/` directory for configuration examples:
- `examples/config_conservative.yaml`
- `examples/config_moderate.yaml`
- `examples/config_aggressive.yaml`

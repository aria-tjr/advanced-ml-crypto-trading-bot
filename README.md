# Advanced ML Crypto Futures Trading Bot

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Security: Updated](https://img.shields.io/badge/security-updated-green.svg)](SECURITY.md)

Professional cryptocurrency futures trading bot with advanced machine learning models for automated trading on Binance, Bybit, and KuCoin.

> **🔒 Security Update (v1.0.2):** All critical vulnerabilities patched. Latest update fixes Keras HDF5 resource allocation vulnerability. See [SECURITY.md](SECURITY.md) for details.

## 🚀 Features

### **Exchange Integration**
- ✅ **Binance Futures** - Full API support with async operations
- ✅ **Bybit Futures** - Unified trading interface
- ✅ **KuCoin Futures** - Complete order management
- 🔄 Real-time data streaming via WebSocket
- 📊 Historical data fetching and caching

### **Machine Learning Models**
- 🌲 **XGBoost** - Gradient boosting for price prediction
- 🧠 **LSTM** - Long Short-Term Memory networks for time series
- 🤖 **Transformer** - Attention-based model for market analysis
- 🎯 **Ensemble** - Combines predictions from all models
- 📈 Cross-validation and walk-forward analysis

### **Technical Indicators (200+)**
- **Trend**: SMA, EMA, MACD, ADX, Parabolic SAR, Supertrend, Aroon
- **Momentum**: RSI, Stochastic, Williams %R, CCI, ROC, CMO, MFI
- **Volatility**: Bollinger Bands, ATR, Keltner Channels, Donchian
- **Volume**: OBV, VWAP, AD, CMF, Volume ratios
- **Patterns**: 30+ candlestick pattern recognition
- **Statistical**: Skewness, Kurtosis, Z-scores, Correlations

### **Market Regime Detection**
- 🔍 Automatic detection of market conditions:
  - Low volatility bullish
  - High volatility bullish
  - Low volatility bearish
  - High volatility bearish
- 📊 Regime-based strategy adaptation
- 🎯 K-means clustering for regime classification

### **Risk Management**
- 💰 **Position Sizing**: Kelly Criterion, Fixed Fractional
- 🛡️ **Stop Loss/Take Profit**: Dynamic and volatility-based
- 📉 **Drawdown Protection**: Max daily loss limits
- ⚖️ **Portfolio Risk**: VaR, CVaR, correlation-adjusted sizing
- 📊 **Performance Metrics**: Sharpe, Sortino, Max Drawdown

### **Backtesting Framework**
- ⏮️ Vectorized backtesting engine
- 📈 Walk-forward analysis
- 💹 Realistic commission and slippage modeling
- 📊 Comprehensive performance analytics
- 🔄 Strategy optimization

### **Data Pipeline**
- 📥 Real-time data fetching
- 💾 Data caching and storage (Parquet format)
- 🔄 Automatic feature engineering
- 🧹 Data cleaning and preprocessing
- 📊 Market data aggregation

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Performance](#performance)
- [Contributing](#contributing)
- [License](#license)

## 🔧 Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Virtual environment (recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/aria-tjr/advanced-ml-crypto-trading-bot.git
cd advanced-ml-crypto-trading-bot
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install TA-Lib (Optional but Recommended)

**Linux/Mac:**
```bash
# Install TA-Lib C library
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install

# Install Python wrapper
pip install TA-Lib
```

**Windows:**
Download pre-built wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib) and install:
```bash
pip install TA_Lib-0.4.XX-cpXX-cpXX-win_amd64.whl
```

### Step 5: Install Package

```bash
pip install -e .
```

## 🚀 Quick Start

### 1. Configure API Keys

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```bash
EXCHANGE_NAME=binance
EXCHANGE_API_KEY=your_api_key_here
EXCHANGE_API_SECRET=your_api_secret_here
EXCHANGE_TESTNET=true  # Start with testnet!
```

### 2. Configure Trading Parameters

Edit `config/config.yaml` to customize trading settings:

```yaml
trading:
  symbols:
    - BTCUSDT
    - ETHUSDT
  timeframe: 1h
  max_positions: 5
  leverage: 10

risk:
  max_position_size: 0.1
  stop_loss_pct: 0.02
  take_profit_pct: 0.04
```

### 3. Train Models

```bash
python examples/train_models.py
```

### 4. Run Backtest

```bash
python examples/run_backtest.py
```

### 5. Start Live Trading

⚠️ **Start with testnet to avoid real losses!**

```bash
python examples/live_trading.py
```

## ⚙️ Configuration

### Exchange Configuration

```yaml
exchange:
  name: binance  # binance, bybit, kucoin
  testnet: true  # Always start with testnet!
  rate_limit: 1200
```

### Trading Parameters

```yaml
trading:
  symbols:
    - BTCUSDT
    - ETHUSDT
  timeframe: 1h  # 1m, 5m, 15m, 1h, 4h, 1d
  max_positions: 5
  leverage: 10
  order_type: LIMIT  # LIMIT, MARKET
```

### Risk Management

```yaml
risk:
  max_position_size: 0.1      # 10% of portfolio per position
  stop_loss_pct: 0.02         # 2% stop loss
  take_profit_pct: 0.04       # 4% take profit
  max_daily_loss: 0.05        # 5% max daily loss
  risk_per_trade: 0.01        # 1% risk per trade
  use_kelly_criterion: true
```

### ML Models

```yaml
ml:
  model_type: ensemble  # xgboost, lstm, transformer, ensemble
  retrain_interval: 24  # hours
  lookback_period: 100
  prediction_horizon: 1
  feature_count: 200
```

## 📚 Usage Examples

### Example 1: Train XGBoost Model

```python
from bot.models.xgboost_model import XGBoostModel
from bot.data.pipeline import DataPipeline

# Initialize data pipeline
pipeline = DataPipeline(exchange, symbols=['BTCUSDT'])
df = await pipeline.prepare_training_data('BTCUSDT')

# Train model
model = XGBoostModel(lookback_period=100)
X, y = model.prepare_data(df)
metrics = model.train(X, y)

# Save model
model.save(Path('models/saved/BTCUSDT'))
```

### Example 2: Run Backtest

```python
from bot.backtest.backtest_engine import BacktestEngine

# Initialize backtest
engine = BacktestEngine(
    initial_capital=10000.0,
    commission=0.0006,
    slippage=0.0001
)

# Run backtest
results = engine.run_backtest(data, signals)
print(f"Total Return: {results['total_return']*100:.2f}%")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
```

### Example 3: Live Trading

```python
from bot.main import TradingBot

# Initialize bot
bot = TradingBot(config_path='config/config.yaml')

# Start trading
await bot.initialize()
await bot.run_strategy()
```

### Example 4: Risk Management

```python
from bot.risk.risk_manager import RiskManager

# Initialize risk manager
risk_manager = RiskManager(
    max_position_size=0.1,
    stop_loss_pct=0.02
)

# Calculate position size
position_size = risk_manager.calculate_position_size(
    account_balance=10000,
    entry_price=50000,
    stop_loss_price=49000
)
```

## 🏗️ Architecture

```
advanced-ml-crypto-trading-bot/
├── src/bot/
│   ├── exchanges/          # Exchange API clients
│   │   ├── base.py        # Abstract base class
│   │   ├── binance.py     # Binance implementation
│   │   ├── bybit.py       # Bybit implementation
│   │   └── kucoin.py      # KuCoin implementation
│   ├── data/              # Data pipeline
│   │   └── pipeline.py    # Data fetching and processing
│   ├── indicators/        # Technical indicators
│   │   └── technical.py   # 200+ indicators
│   ├── models/            # ML models
│   │   ├── xgboost_model.py
│   │   ├── lstm_model.py
│   │   └── transformer_model.py
│   ├── strategy/          # Trading strategies
│   │   └── regime_detection.py
│   ├── risk/              # Risk management
│   │   └── risk_manager.py
│   ├── backtest/          # Backtesting
│   │   └── backtest_engine.py
│   ├── config.py          # Configuration management
│   └── main.py            # Main bot orchestrator
├── config/                # Configuration files
├── examples/              # Usage examples
├── tests/                 # Unit tests
├── data/                  # Data storage
├── models/                # Saved models
├── logs/                  # Log files
├── requirements.txt       # Dependencies
├── setup.py              # Package setup
└── README.md             # This file
```

## 🔌 API Documentation

### Exchange Interface

All exchanges implement the `BaseExchange` interface:

```python
class BaseExchange(ABC):
    async def connect() -> None
    async def disconnect() -> None
    async def get_balance() -> Dict[str, float]
    async def get_positions() -> List[Dict[str, Any]]
    async def get_historical_data(...) -> pd.DataFrame
    async def place_order(...) -> Dict[str, Any]
    async def cancel_order(...) -> Dict[str, Any]
    async def get_ticker(...) -> Dict[str, float]
    async def get_orderbook(...) -> Dict[str, List]
```

### Model Interface

All ML models implement similar training and prediction methods:

```python
class Model:
    def prepare_data(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]
    def train(X: np.ndarray, y: np.ndarray) -> Dict
    def predict(X: np.ndarray) -> np.ndarray
    def save(path: Path) -> None
    def load(path: Path) -> None
```

## 🧪 Testing

Run the test suite:

```bash
pytest tests/ -v --cov=bot
```

Run specific test:

```bash
pytest tests/test_xgboost.py -v
```

## 📊 Performance

Example backtest results on BTC/USDT (2023):

- **Total Return**: 45.3%
- **Sharpe Ratio**: 2.1
- **Max Drawdown**: -8.5%
- **Win Rate**: 58%
- **Profit Factor**: 1.8
- **Total Trades**: 247

*Past performance is not indicative of future results.*

## ⚠️ Risk Disclaimer

**IMPORTANT**: Cryptocurrency trading carries substantial risk of loss. This software is provided for educational purposes only. 

- Never trade with money you cannot afford to lose
- Always start with testnet/paper trading
- Thoroughly backtest strategies before live trading
- Monitor your bot regularly
- Use appropriate risk management
- Understand all code before deployment

The authors are not responsible for any financial losses incurred through the use of this software.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- TA-Lib for technical analysis
- CCXT for exchange connectivity
- XGBoost, PyTorch, TensorFlow for ML
- The open-source crypto trading community

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/aria-tjr/advanced-ml-crypto-trading-bot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/aria-tjr/advanced-ml-crypto-trading-bot/discussions)

## 🗺️ Roadmap

- [ ] Add more exchanges (Kraken, OKX, Gate.io)
- [ ] Implement reinforcement learning models
- [ ] Add sentiment analysis from news/social media
- [ ] Web dashboard for monitoring
- [ ] Mobile app for alerts
- [ ] Advanced order types (trailing stops, etc.)
- [ ] Portfolio optimization
- [ ] Multi-timeframe analysis

---

**Made with ❤️ by the Advanced ML Trading Bot Team**

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2024-01-17

### Security

#### Critical Security Updates
- Updated `aiohttp` from 3.9.0 to 3.13.3
  - Fixed HTTP Parser zip bomb vulnerability
  - Fixed Denial of Service from malformed POST requests
  - Fixed directory traversal vulnerability
  
- Updated `torch` from 2.1.0 to 2.6.0
  - Fixed heap buffer overflow vulnerability
  - Fixed use-after-free vulnerability
  - Fixed remote code execution via torch.load
  - Fixed deserialization vulnerability

- Updated `lightgbm` from 4.1.0 to 4.6.0
  - Fixed remote code execution vulnerability

#### High Security Updates
- Updated `keras` from 2.14.0 to 3.12.0
  - Fixed directory traversal vulnerabilities
  - Fixed path traversal in keras.utils.get_file
  - Fixed deserialization of untrusted data
  - Fixed arbitrary code execution vulnerability

- Updated `transformers` from 4.35.0 to 4.48.0
  - Fixed multiple deserialization of untrusted data vulnerabilities

### Changed
- All dependency versions updated to patched versions
- No breaking changes to existing functionality
- Improved overall security posture

### Documentation
- Added SECURITY.md with vulnerability details and migration guide
- Updated installation instructions for secure versions

## [1.0.0] - 2024-01-17

### Added

#### Exchange Integration
- Binance Futures API client with full order management
- Bybit Futures API client with unified trading interface
- KuCoin Futures API client with complete functionality
- Unified exchange interface for seamless switching
- Real-time data streaming support
- Historical data fetching with caching

#### ML Models
- XGBoost model for gradient boosting predictions
- LSTM model for time series analysis
- Transformer model with attention mechanism
- Ensemble model combining all three models
- Cross-validation framework
- Walk-forward analysis support

#### Technical Indicators
- 200+ technical indicators including:
  - 50+ trend indicators (SMA, EMA, MACD, ADX, etc.)
  - 50+ momentum indicators (RSI, Stochastic, CCI, etc.)
  - 40+ volatility indicators (Bollinger Bands, ATR, etc.)
  - 30+ volume indicators (OBV, VWAP, CMF, etc.)
  - 30+ candlestick patterns
  - 20+ statistical indicators

#### Market Regime Detection
- K-means clustering for regime classification
- 4 market regimes: low/high volatility × bullish/bearish
- Volatility clustering
- Trend detection algorithms
- Regime statistics and transitions

#### Risk Management
- Kelly Criterion for optimal position sizing
- Fixed fractional position sizing
- Dynamic stop loss based on volatility
- Take profit with risk-reward ratios
- Daily loss limits
- Portfolio correlation adjustments
- VaR and CVaR calculations
- Sharpe and Sortino ratios

#### Backtesting Framework
- Vectorized backtesting engine
- Realistic commission and slippage modeling
- Walk-forward analysis
- Comprehensive performance metrics
- Trade-by-trade analysis
- Equity curve visualization

#### Data Pipeline
- Real-time data fetching
- Data caching and storage (Parquet)
- Automatic feature engineering
- Data cleaning and preprocessing
- Market data aggregation

#### Configuration
- YAML-based configuration
- Environment variable support
- Multiple risk profiles (conservative, moderate, aggressive)
- Exchange-specific settings
- Flexible parameter tuning

#### Documentation
- Comprehensive README with examples
- Installation guide
- Configuration guide
- Trading guide
- API documentation
- Contributing guidelines

#### Examples
- Model training example
- Backtesting example
- Live trading example
- Quick start script with interactive menu

#### Utilities
- Price and percentage formatting
- Return calculations
- Drawdown analysis
- Timestamp conversions
- JSON data handling

### Security
- API key encryption support
- IP whitelisting recommendations
- Testnet-first approach
- Daily loss limits
- Position size limits

## [Unreleased]

### Planned Features
- Additional exchanges (Kraken, OKX, Gate.io)
- Reinforcement learning models
- Sentiment analysis integration
- Web dashboard for monitoring
- Mobile app for alerts
- Advanced order types
- Portfolio optimization
- Multi-timeframe analysis
- Telegram bot integration
- Docker support
- CI/CD pipeline

---

For a detailed comparison between releases, see the [full diff](https://github.com/aria-tjr/advanced-ml-crypto-trading-bot/compare/v0.1.0...v1.0.0).

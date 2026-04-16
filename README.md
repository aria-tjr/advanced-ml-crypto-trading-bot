# Advanced ML Crypto Trading Bot

> **Status: 🚧 Work In Progress — Code refactoring in progress. Full release coming soon.**

Professional cryptocurrency futures trading bot with advanced ML models for automated trading on Binance, Bybit, and KuCoin.

## Planned Features

- **XGBoost & LSTM models** for price direction prediction
- **Transformer-based** time-series forecasting
- Multi-exchange support: Binance, Bybit, KuCoin
- Risk management: position sizing, stop-loss, take-profit
- Backtesting engine with historical data
- Telegram notifications for trade signals
- Docker deployment

## Tech Stack

- Python 3.10+
- scikit-learn, XGBoost, TensorFlow/Keras
- CCXT (exchange API wrapper)
- Freqtrade framework
- PostgreSQL (trade logging)
- Docker + Docker Compose

## Related Work

This bot builds on top of experience from:
- A live Freqtrade-based crypto trading bot with RSI, MACD, and channel pattern analysis (2023–2024)
- Real deployment experience with signal bots serving Telegram communities

## Progress

- [x] Strategy design and backtesting framework
- [x] Technical indicator pipeline (EMA, RSI, MACD, Bollinger Bands, ATR)  
- [ ] ML model training pipeline (in progress)
- [ ] Live trading integration
- [ ] Documentation and setup guides

---
*Repository is actively being developed. Star to follow progress.*

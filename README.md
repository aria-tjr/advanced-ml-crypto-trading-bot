# Advanced ML Crypto Trading Bot

A production-oriented cryptocurrency futures trading bot combining XGBoost, LSTM, and Transformer models for multi-exchange automated trading on Binance, Bybit, and KuCoin.

## Highlights

- **Multi-model ensemble** — XGBoost (classification), LSTM (sequence modeling), and Transformer (long-range dependencies) combined into a single signal score
- **Multi-exchange** via CCXT — Binance, Bybit, KuCoin (spot and perpetual futures)
- **Walk-forward backtesting** with Sharpe ratio, max drawdown, win rate, and profit factor
- **Risk management** — dynamic position sizing, ATR-based stops, daily drawdown cutoff
- **Operational tooling** — Telegram alerts, Docker deployment, PostgreSQL trade logging

## Tech Stack

- Python 3.10+
- scikit-learn, XGBoost, TensorFlow/Keras, PyTorch
- CCXT (exchange API wrapper)
- Freqtrade framework (strategy runner)
- PostgreSQL (trade logging)
- Docker + Docker Compose

## Architecture

```
data/          OHLCV ingestion + feature engineering
indicators/    EMA, RSI, MACD, Bollinger Bands, ATR, volume profile
models/        XGBoost / LSTM / Transformer training + inference
backtest/      Walk-forward engine with realistic slippage + fees
risk/          Position sizing, stop-loss, max-drawdown cutoff
execution/     CCXT-based live order routing
notify/        Telegram + log handlers
```

## Status

Core modules (data pipeline, indicator engine, backtester, risk layer) are complete and tested. The ML ensemble and live-execution layer are being hardened for production use. Backtest reports and sample outputs available on request.

## Related Work

Built on real deployment experience:

- A live Freqtrade-based trading bot with RSI / MACD / channel-pattern strategies (2023–2024)
- Telegram signal bots serving active trading communities
- [NEXUS](https://github.com/aria-tjr/111) — 7-layer PyTorch crypto signal engine

## Disclaimer

This software is provided for research and educational purposes. Cryptocurrency markets are highly volatile; no trading strategy guarantees profit. Never deploy capital you cannot afford to lose, and always paper-trade new configurations before going live.

## License

MIT

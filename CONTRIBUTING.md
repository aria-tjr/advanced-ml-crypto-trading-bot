# Contributing to Advanced ML Crypto Trading Bot

Thank you for considering contributing to this project! 🎉

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the technical aspects
- Help others learn and grow

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported
2. Use the bug report template
3. Include detailed information:
   - Python version
   - Operating system
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages and logs

### Suggesting Features

1. Check if the feature has been requested
2. Describe the feature clearly
3. Explain the use case
4. Consider implementation complexity

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Write/update tests
5. Update documentation
6. Commit with clear messages
7. Push to your fork
8. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/advanced-ml-crypto-trading-bot.git
cd advanced-ml-crypto-trading-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Code Style

### Python Style Guide

We follow PEP 8 with some modifications:

- Line length: 100 characters
- Use type hints
- Write docstrings for all functions
- Use f-strings for formatting

### Example

```python
def calculate_position_size(
    account_balance: float,
    entry_price: float,
    stop_loss_price: float
) -> float:
    """
    Calculate optimal position size.
    
    Args:
        account_balance: Current account balance
        entry_price: Entry price for position
        stop_loss_price: Stop loss price
        
    Returns:
        Position size in base currency
    """
    risk_amount = account_balance * 0.01
    price_risk = abs(entry_price - stop_loss_price) / entry_price
    return risk_amount / price_risk
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=bot --cov-report=html

# Run specific test
pytest tests/test_xgboost.py -v
```

### Writing Tests

```python
import pytest
from bot.models.xgboost_model import XGBoostModel

def test_xgboost_training():
    """Test XGBoost model training"""
    model = XGBoostModel()
    # ... test code
    assert model is not None
```

## Documentation

### Docstrings

Use Google style docstrings:

```python
def function_name(param1: type, param2: type) -> return_type:
    """
    Brief description.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: Description of when this is raised
    """
```

### README Updates

Update README.md when:
- Adding new features
- Changing configuration
- Updating dependencies
- Modifying installation steps

## Commit Messages

Use clear, descriptive commit messages:

```
feat: Add LSTM model for time series prediction
fix: Correct position sizing calculation
docs: Update installation guide
test: Add tests for risk manager
refactor: Simplify data pipeline code
```

Prefixes:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `chore`: Maintenance

## Project Structure

```
src/bot/
├── exchanges/      # Exchange API clients
├── data/          # Data pipeline
├── indicators/    # Technical indicators
├── models/        # ML models
├── strategy/      # Trading strategies
├── risk/          # Risk management
├── backtest/      # Backtesting
└── utils/         # Utilities
```

## Adding New Features

### New Exchange

1. Create `src/bot/exchanges/new_exchange.py`
2. Inherit from `BaseExchange`
3. Implement all required methods
4. Add tests
5. Update documentation

### New ML Model

1. Create `src/bot/models/new_model.py`
2. Implement `train()`, `predict()`, `save()`, `load()`
3. Add to ensemble if applicable
4. Add tests and examples
5. Update documentation

### New Indicator

1. Add to `src/bot/indicators/technical.py`
2. Follow existing pattern
3. Include in `calculate_all()`
4. Test on sample data
5. Document usage

## Review Process

Pull requests will be reviewed for:

1. **Functionality**: Does it work as intended?
2. **Tests**: Are there adequate tests?
3. **Documentation**: Is it documented?
4. **Code Quality**: Does it follow style guide?
5. **Performance**: Is it efficient?
6. **Security**: Are there security issues?

## Getting Help

- 📖 Read the [documentation](../README.md)
- 💬 Join [discussions](https://github.com/aria-tjr/advanced-ml-crypto-trading-bot/discussions)
- 🐛 Check [issues](https://github.com/aria-tjr/advanced-ml-crypto-trading-bot/issues)
- 📧 Contact maintainers

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🚀

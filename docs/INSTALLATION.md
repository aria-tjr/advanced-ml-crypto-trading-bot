# Installation Guide

## System Requirements

- **Operating System**: Linux, macOS, or Windows 10+
- **Python**: 3.9 or higher
- **RAM**: Minimum 8GB (16GB recommended for ML training)
- **Storage**: 10GB free space
- **Internet**: Stable broadband connection

## Detailed Installation Steps

### 1. Python Installation

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.9 python3.9-venv python3-pip
```

#### macOS
```bash
brew install python@3.9
```

#### Windows
Download from [python.org](https://www.python.org/downloads/)

### 2. Clone Repository

```bash
git clone https://github.com/aria-tjr/advanced-ml-crypto-trading-bot.git
cd advanced-ml-crypto-trading-bot
```

### 3. Virtual Environment

```bash
# Create virtual environment
python3.9 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### 5. Install TA-Lib

#### Linux
```bash
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
cd ..
pip install TA-Lib
```

#### macOS
```bash
brew install ta-lib
pip install TA-Lib
```

#### Windows
1. Download wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib)
2. Install: `pip install TA_Lib-0.4.XX-cpXX-cpXX-win_amd64.whl`

### 6. Install Package

```bash
pip install -e .
```

### 7. Verify Installation

```bash
python -c "import bot; print('Installation successful!')"
```

## Troubleshooting

### TA-Lib Installation Issues

If you encounter issues installing TA-Lib:

**Option 1**: Skip TA-Lib (will use pandas-ta instead)
```bash
pip install -r requirements.txt --no-deps
pip install pandas-ta
```

**Option 2**: Use Docker (see Docker guide)

### PyTorch Installation

For GPU support:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

For CPU only:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Permission Errors

On Linux/Mac, use:
```bash
sudo pip install -r requirements.txt
```

Or install in user directory:
```bash
pip install --user -r requirements.txt
```

## Docker Installation

### Build Image

```bash
docker build -t crypto-trading-bot .
```

### Run Container

```bash
docker run -d \
  --name trading-bot \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/logs:/app/logs \
  crypto-trading-bot
```

## Next Steps

After installation:
1. Configure API keys (see [Configuration Guide](CONFIGURATION.md))
2. Run backtests (see [Usage Examples](EXAMPLES.md))
3. Start live trading (see [Trading Guide](TRADING.md))

# TinyShare

A lightweight wrapper for tushare financial data API that provides the exact same interface as tushare but with additional features and optimizations.

## Installation

```bash
pip install tinyshare
```

## Usage

TinyShare provides the exact same API as tushare, so you can simply replace your import statement:

```python
# Instead of: import tushare as ts
import tinyshare as ts

# Set your token
ts.set_token('your_tushare_token_here')
pro = ts.pro_api()

# Get index daily data
df = pro.index_daily(
    ts_code='000001.SH',
    start_date='20250621',
    end_date='20250628'
)

print(df)
```

## New Features

### Free Minute Data with stk_mins_tiny

TinyShare now provides a free alternative to tushare's `stk_mins` interface using baostock data:

```python
import tinyshare as ts

# Get minute data for free (no tushare credits needed)
df = ts.stk_mins_tiny(
    ts_code='600000.SH',
    freq='5min',
    start_date='2023-08-25',
    end_date='2023-08-25'
)

print(df.head())
```

**Key Features:**
- 🆓 **Free**: No tushare credits required
- 📊 **Multiple frequencies**: 1min, 5min, 15min, 30min, 60min
- 🔄 **Format compatibility**: Returns tushare-compatible format by default
- 📈 **Rich history**: Access to years of historical minute data
- 🎯 **Dual format**: Support both tushare format and raw baostock format

**Supported Parameters:**
- `ts_code`: Stock code (e.g., '600000.SH', '000001.SZ')
- `freq`: Frequency ('1min', '5min', '15min', '30min', '60min')
- `start_date`: Start date (optional)
- `end_date`: End date (optional)
- `origin`: Return raw baostock format when True (default: False)

## Features

- **100% API Compatible**: Drop-in replacement for tushare
- **Enhanced Token Management**: Support for both tokens and extract codes
- **Free Minute Data**: Get minute-level data without tushare credits
- **Enhanced Error Handling**: Better error messages and debugging
- **Performance Optimizations**: Caching and request optimization
- **Easy Migration**: Simply change your import statement

## Requirements

- Python 3.7+
- tushare>=1.2.0
- pandas>=1.0.0
- baostock>=0.8.0

## Examples

### Basic Usage
```python
import tinyshare as ts

# Set token (supports both regular tokens and extract codes)
ts.set_token('your_token_here')
pro = ts.pro_api()

# Get stock data
df = pro.daily(ts_code='000001.SZ', start_date='20240101', end_date='20240131')
```

### Free Minute Data
```python
import tinyshare as ts

# Get 5-minute data for the last week
df = ts.stk_mins_tiny('600000.SH', '5min')

# Get 1-minute data for specific date range
df = ts.stk_mins_tiny('000001.SZ', '1min', '2023-08-25', '2023-08-25')

# Get raw baostock format
df_raw = ts.stk_mins_tiny('600000.SH', '5min', origin=True)
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 
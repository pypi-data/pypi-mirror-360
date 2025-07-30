# Technical Trading Strategy Prototyper

TA-based trading is a visual endeavour and should be practiced as such.
This package provides the means to chart each round-trip trade from a backtest, allowing you to refine your strategy directly based on charts and thus remain in the visual workflow that defines technical analysis.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Development Status](https://img.shields.io/badge/status-pre--alpha-red.svg)](https://pypi.org/project/ttsprototyper/)

---

## ⚠️ Disclaimer

THE INFORMATION PROVIDED IS FOR EDUCATIONAL AND INFORMATIONAL PURPOSES ONLY. IT DOES NOT CONSTITUTE FINANCIAL, INVESTMENT, OR TRADING ADVICE. TRADING INVOLVES SUBSTANTIAL RISK, AND YOU MAY LOSE MORE THAN YOUR INITIAL INVESTMENT.

THIS SOFTWARE AND ITS DOCUMENTATION PAGES ARE PROVIDED "AS IS," WITHOUT ANY WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE. THE AUTHORS AND COPYRIGHT HOLDERS ASSUME NO LIABILITY FOR ANY CLAIMS, DAMAGES, OR OTHER LIABILITIES ARISING FROM THE USE OR DISTRIBUTION OF THIS SOFTWARE OR DOCUMENTATION PAGES. USE AT YOUR OWN RISK. THIS SOFTWARE AND ITS DOCUMENTATION PAGES ARE LICENSED UNDER THE GNU GENERAL PUBLIC LICENSE V3.0 (GPL-3.0). SEE THE GPL-3.0 FOR DETAILS.

---

## Table of Contents

- [Installation](#installation)
- [Core Concepts](#core-concepts)
- [Order Types](#order-types)
- [Position Management](#position-management)
- [Strategy Implementation](#strategy-implementation)
- [Trade Analysis & Statistics](#trade-analysis--statistics)
- [Charting & Visualization](#charting--visualization)
- [Output Files & Folders](#output-files--folders)
- [Complete Example](#complete-example)
- [Advanced Features](#advanced-features)
- [Trading Hours & Restrictions](#trading-hours--restrictions)
- [Dependencies](#dependencies)

## Installation

### From PyPI (Recommended)

```bash
pip install ttsprototyper
```

### For Google Colab

```python
!pip install ttsprototyper

# Optional: Mount Google Drive for CSV access and persistent storage
from google.colab import drive
drive.mount('/content/drive')

# Change to your Google Drive directory for persistent file storage
import os
os.chdir('/content/drive/MyDrive/trading_analysis')  # Adjust path as needed
```

**Note for Colab Users**: The prototyper creates a `backtest/` folder structure in the current working directory. In Colab:
- Files saved to `/content/` are temporary and will be lost when the session ends
- To persist your charts and analysis, change to a Google Drive directory before running your strategy
- All chart files (PNG format) and analysis will be saved to your Google Drive for permanent access

### Development Installation

```bash
git clone https://github.com/nilskujath/ttsprototyper.git
cd ttsprototyper
poetry install
```

## Core Concepts

### Architecture

The package is built around a single abstract base class `TTSPrototyper` that encapsulates the entire backtesting workflow. Users implement custom strategies by subclassing `TTSPrototyper` and defining three required methods:

* `calculate_indicators(self) -> pd.DataFrame`: Calculate any technical indicators you want to use in your strategy.
* `generate_signals(self) -> pd.DataFrame`: Define your trading signals based on these indicators.
* `apply_strategy_rules(self, row)`: Implement your trading logic based on these signals for each bar.

Note: From the perspective of the backtester, there is no functional difference between a (complex) indicator and a signal. However, we conceptually separate indicators and signals to enforce different naming conventions that will later be used in charting your trades.

### Naming Conventions

#### Indicators

Indicators must follow a specific naming pattern for chart plotting:

```python
# Format: "I<2-digit-number>_<indicator_name>"
self._market_data_df["I00_sma_50"] = ...    # Plots on price chart
self._market_data_df["I01_rsi"] = ...       # Plots in subplot 1
self._market_data_df["I01_rsi_ma"] = ...    # Also plots in subplot 1
self._market_data_df["I02_macd"] = ...      # Plots in subplot 2
```

- `I00_*`: Overlays on the main price chart
- `I01_*`, `I02_*`, etc.: Groups indicators in separate subplots

#### Signals

Signals must also follow a specific naming pattern for chart plotting:

```python
# Format: "S<2-digit-number>_<signal_name>"
self._market_data_df["S00_fast_entry"] = ...    
self._market_data_df["S01_short_on_high"] = ... 
```

The two-digit number is used to indicate the type of signal. The following types are defined: 

**Entry Signals**

* `S00_*`: Long-entry signals: If met, a position should be entered long
* `S01_*`: Short-entry signals: If met, a position should be entered short

**Increase Exposure Signals**

* `S02_*`: Add-if-long-position signals: If met, increase exposure of long position 
* `S03_*`: Add-if-short-position signals: If met, increase exposure of short position

**Reduce Exposure Signals**

* `S04_*`: Reduce-if-long-position signals: If met, reduce exposure of long position 
* `S05_*`: Reduce-if-short-position signals: If met, reduce exposure of short position 

**Exit Signals**

* `S06_*`: Stop-loss signals: If met, exit remaining position for a loss
* `S07_*`: Take-profit signals: If met, exit remaining position for a profit
* `S08_*`: Emergency-exit signals: If met, exit remaining position immediately at a loss or a profit

Any two-digit number greater than 08 is reserved for custom signals that do not fit into the above categories and plotted on the chart with a generic symbol.


### Flow of Data

#### Central Dataframes

The backtester maintains two central dataframes: `_market_data_df` and `_fills_df`.
Upon initialization, the `_market_data_df` is populated with the raw market data from the CSV file and, if the relevant arguments are provided, filtered for a specific symbol and limited to a maximum number of bars.

```python
import ttsprototyper as ttsp
import pandas as pd
import logging

class MyTTSPrototyper(ttsp.TTSPrototyper):
    def calculate_indicators(self) -> pd.DataFrame:
        pass

    def generate_signals(self) -> pd.DataFrame:
        pass

    def apply_strategy_rules(self, row):
        pass


def main():
    prototyper = MyTTSPrototyper(
        path_to_csv="path/to/csv",
        filter_for_symbol="SYMBOL",
        max_bars=1000,
        log_level=logging.DEBUG,
    )

if __name__ == "__main__":
    main()
```

* Filtering for a symbol might be necessary if the CSV file contains OHLCV data for the same time period for multiple symbols (common when backtesting on futures data, where CSV files can contain also non front-month contracts).
* Limiting the number of bars is useful for testing and debugging purposes, as it allows you to quickly iterate on your strategy without having to wait for the backtester to process a large amount of data.

#### Supported CSV Format

The backtester expects CSV data in [Databento](https://databento.com/)-style format with the following columns:
- `ts_event`: Timestamp (nanoseconds)
- `rtype`: Record type (32=1s, 33=1m, 34=1h, 35=1d bars)
- `open`, `high`, `low`, `close`: OHLC prices (scaled by 1e9)
- `volume`: Trading volume
- `symbol`: Instrument symbol

The record type is used to determine the time period of the bars. The backtester currently supports 1s, 1m, 1h, and 1d bars.
It is important that the data ingested via the CSV is of a single record type only.


#### Contract Specifications

After initializing the subclassed `TTSPrototyper`, you must specify the contract specifications for the instrument you are trading via the `set_contract_specifications` method.

```python
...

def main():
    prototyper = MyTTSPrototyper(
        path_to_csv="path/to/csv",
        filter_for_symbol="SYMBOL",
        max_bars=1000,
    )
    
    prototyper.set_contract_specifications(
        point_value=2.0,
        tick_size=0.25,
        broker_commission_per_contract=0.25,
        exchange_fees_per_contract=0.37,
        minimum_fees=0.0,
    )

if __name__ == "__main__":
    main()
```

Setting the contract specifications is necessary to calculate performance metrics (including commissions and fees) and simulate fills (tick size is important to simulate realistic fills; if you are trading stocks, you can set tick size to 0.01, unless your stock is penny stock, in which case you should probably set it to 0.0001).


### Running the Backtest

After the `set_contract_specifications` method has run, you can run the backtest by calling the `run` method.
Internally, the `run` method calls your `calculate_indicators`, `generate_signals`, and `apply_strategy_rules` methods.

```python
import ttsprototyper as ttsp
import pandas as pd
import logging


class MyTTSPrototyper(ttsp.TTSPrototyper):
    def calculate_indicators(self) -> pd.DataFrame:
        # 20-Period SMA
        self._market_data_df["I00_sma_20"] = (
            self._market_data_df["close"].rolling(20).mean()
        )
        # 100-Period SMA
        self._market_data_df["I00_sma_100"] = (
            self._market_data_df["close"].rolling(100).mean()
        )

        return self._market_data_df

    def generate_signals(self) -> pd.DataFrame:
        # Long entry signal
        # First check for valid data (no NaN values)
        valid_rows_S00 = (
                pd.notna(self._market_data_df["I00_sma_20"])
                & pd.notna(self._market_data_df["I00_sma_100"])
        )

        # Initialize signal column with zeros
        self._market_data_df["S00_long_entry"] = 0

        # Set signal to 1 where conditions are met
        self._market_data_df.loc[
            valid_rows_S00
            & (self._market_data_df["close"] > self._market_data_df["I00_sma_20"])
            & (self._market_data_df["I00_sma_20"] > self._market_data_df[
                "I00_sma_100"]),
            "S00_long_entry"
        ] = 1

        # Exit signal
        # First check for valid data (no NaN values)
        valid_rows_S08 = (
                pd.notna(self._market_data_df["I00_sma_20"])
                & pd.notna(self._market_data_df["I00_sma_100"])
        )

        # Initialize signal column with zeros
        self._market_data_df["S08_exit"] = 0

        # Set signal to 1 where conditions are met
        self._market_data_df.loc[
            valid_rows_S08
            & (self._market_data_df["close"] < self._market_data_df["I00_sma_20"])
            & (self._market_data_df["I00_sma_20"] < self._market_data_df[
                "I00_sma_100"]),
            "S08_exit"
        ] = 1

        return self._market_data_df

    def apply_strategy_rules(self, row):
        pass


def main():
    prototyper = MyTTSPrototyper(
        path_to_csv="path/to/csv",
        filter_for_symbol="SYMBOL",
        max_bars=1000,
        log_level=logging.DEBUG,
    )

    prototyper.set_contract_specifications(
        point_value=2.0,
        tick_size=0.25,
        broker_commission_per_contract=0.25,
        exchange_fees_per_contract=0.37,
        minimum_fees=0.0,
    )

    prototyper.run()

if __name__ == "__main__":
    main()
```




## Order Types

The prototyper supports three types of orders for realistic trading simulation:

### MarketOrder
Executes immediately at the current market price (open price of the next bar).

```python
import uuid
from ttsprototyper import MarketOrder, Side

# Buy 2 contracts at market
buy_order = MarketOrder(
    order_id=uuid.uuid4(),
    ts_event=current_timestamp,
    order_direction=Side.BUY,
    quantity=2.0
)
strategy.submit_order(buy_order)
```

### LimitOrder
Executes only if the market reaches the specified limit price or better.

```python
from ttsprototyper import LimitOrder

# Buy 1 contract only if price drops to 4500 or lower
limit_order = LimitOrder(
    order_id=uuid.uuid4(),
    ts_event=current_timestamp,
    order_direction=Side.BUY,
    quantity=1.0,
    limit_price=4500.0
)
strategy.submit_order(limit_order)
```

### StopOrder
Becomes a market order when the stop price is reached (used for stop-losses and breakouts).

```python
from ttsprototyper import StopOrder

# Sell 1 contract if price falls to 4450 (stop-loss)
stop_order = StopOrder(
    order_id=uuid.uuid4(),
    ts_event=current_timestamp,
    order_direction=Side.SELL,
    quantity=1.0,
    stop_price=4450.0
)
strategy.submit_order(stop_order)
```

## Position Management

The prototyper uses **FIFO (First In, First Out)** accounting for position management:

- **Positions**: Individual entries are tracked separately
- **Trades**: Complete round trips from flat to flat position
- **Commission Tracking**: Accurate commission and fee calculations
- **Break-even Prices**: Automatic calculation of commission-adjusted break-even levels

### Position Tracking
```python
# Get current net position
current_position = strategy.get_current_position()

# Get detailed position information
positions = strategy.get_positions()

# Check if currently flat
is_flat = strategy.get_current_position() == 0
```

## Strategy Implementation

### apply_strategy_rules Method

The `apply_strategy_rules` method is where you implement your trading logic. It's called for each bar during backtesting:

```python
def apply_strategy_rules(self, row):
    """Apply strategy rules for the current bar and submit orders if needed.

    Args:
        row: Current bar data (pandas Series-like object) with attributes:
             - ts_event: Timestamp
             - open, high, low, close: OHLC prices
             - volume: Trading volume
             - position: Current net position
             - All your indicators (I00_*, I01_*, etc.)
             - All your signals (S00_*, S01_*, etc.)
    """
    current_position = self.get_current_position()

    # Example: Enter long position
    if row.S00_long_entry == 1 and current_position == 0:
        order = MarketOrder(
            order_id=uuid.uuid4(),
            ts_event=row.ts_event,
            order_direction=Side.BUY,
            quantity=1.0
        )
        self.submit_order(order)

    # Example: Exit position
    elif row.S08_exit == 1 and current_position > 0:
        order = MarketOrder(
            order_id=uuid.uuid4(),
            ts_event=row.ts_event,
            order_direction=Side.SELL,
            quantity=abs(current_position)
        )
        self.submit_order(order)
```

### Signal-Based Trading Logic

Use your predefined signals to make trading decisions:

```python
def apply_strategy_rules(self, row):
    current_pos = self.get_current_position()

    # Entry signals
    if row.S00_long_entry == 1 and current_pos == 0:
        # Enter long position
        pass
    elif row.S01_short_entry == 1 and current_pos == 0:
        # Enter short position
        pass

    # Add to position signals
    elif row.S02_add_long == 1 and current_pos > 0:
        # Add to long position
        pass

    # Reduce position signals
    elif row.S04_reduce_long == 1 and current_pos > 0:
        # Reduce long position
        pass

    # Exit signals
    elif row.S06_stop_loss == 1 and current_pos != 0:
        # Stop loss exit
        pass
    elif row.S07_take_profit == 1 and current_pos != 0:
        # Take profit exit
        pass
```

## Trade Analysis & Statistics

The prototyper provides comprehensive trade analysis and performance statistics:

### Basic Statistics
```python
# Get trade counts
trade_stats = strategy.get_trade_count()
print(f"Total trades: {trade_stats['total_completed']}")
print(f"Winning trades: {trade_stats['winning']}")
print(f"Losing trades: {trade_stats['losing']}")

# Get completed trades as DataFrame
trades_df = strategy.get_trades_dataframe()
```

### Performance Metrics
The `print_backtest_results()` method provides a comprehensive performance report including:

- **Trade Statistics**: Total, winning, losing, and open trades
- **P&L Analysis**: Gross P&L, commissions, net P&L
- **Win/Loss Metrics**: Average winner/loser, win rate, profit factor
- **Risk Metrics**: Biggest winner/loser, risk-reward ratio
- **Trade Duration**: Average holding time
- **Consecutive Trades**: Max consecutive wins/losses

```python
# Print comprehensive backtest results
strategy.print_backtest_results(
    strategy_name="My Strategy",
    contract_name="MNQ"
)
```

### MAE/MFE Analysis
Maximum Adverse Excursion (MAE) and Maximum Favorable Excursion (MFE) analysis helps optimize stop-loss and take-profit levels:

- **MAE**: Tracks the worst unrealized loss during each trade
- **MFE**: Tracks the best unrealized profit during each trade
- **Points-based**: All measurements in points rather than dollars
- **Winning Trade Analysis**: Shows how much winning trades went against you before becoming profitable

## Charting & Visualization

The prototyper generates multiple types of charts for comprehensive trade analysis:

### Individual Trade Charts
```python
# Generate charts for each completed trade
strategy.generate_trade_charts(
    lookback_bars=50,    # Bars to show before entry
    lookforward_bars=50  # Bars to show after exit
)
```

Each trade chart includes:
- **OHLC Price Data**: High-low bars with close price markers
- **Technical Indicators**: Overlaid on price chart and in subplots
- **Trade Markers**: Entry/exit points with color-coded P&L
- **Position Tracking**: Visual representation of position size
- **P&L Tracking**: Real-time unrealized P&L during the trade
- **Trade Statistics**: Overlay with key metrics

### Equity Curve Analysis
Comprehensive equity curve charts showing:
- **Net P&L**: Cumulative profit/loss after commissions
- **Gross P&L**: Cumulative profit/loss before commissions
- **Drawdown Analysis**: Underwater curves and maximum drawdown
- **Performance Statistics**: Win rate, profit factor, risk-reward ratio

### MAE/MFE Scatter Plot
Scatter plot analysis showing:
- **Winning Trades**: Green dots showing MAE vs MFE
- **Losing Trades**: Red dots showing maximum movements
- **Breakeven Trades**: Yellow dots for neutral outcomes
- **Optimal Levels**: Visual identification of stop-loss and take-profit zones

### Trade Journey Chart
Bar chart showing for each trade:
- **Maximum Upward Movement**: Highest point reached from entry
- **Maximum Downward Movement**: Lowest point reached from entry
- **Final Exit Point**: Actual exit level in points
- **Movement Analysis**: Understanding of trade development patterns

## Output Files & Folders

The prototyper automatically creates a structured output directory for all analysis:

```
backtest/
├── trade_charts/           # Individual trade charts
│   ├── trade_001.png      # Chart for trade #1
│   ├── trade_002.png      # Chart for trade #2
│   └── ...
├── biggest_winners/        # Top performing trades
│   ├── winner_01_trade_015_pnl_125.50.png
│   └── ...
├── biggest_losers/         # Worst performing trades
│   ├── loser_01_trade_008_pnl_-89.25.png
│   └── ...
└── stats/                  # Performance analysis charts
    ├── equity_curve.png    # Equity curve with drawdown
    ├── mae_mfe_analysis.png # MAE vs MFE scatter plot
    └── trade_journey.png   # Trade journey bar chart
```

### Automatic Cleanup
The prototyper automatically cleans up existing backtest folders before generating new results, ensuring each run starts fresh without mixing old and new data.

### Google Colab Considerations
When using Google Colab:
- **File Persistence**: Change to a Google Drive directory before running to ensure charts are saved permanently
- **File Access**: All generated PNG files can be downloaded directly from the Colab file browser
- **Directory Structure**: The `backtest/` folder will be created in your current working directory
- **Memory Management**: Large datasets may require runtime restarts; charts are saved incrementally

## Complete Example

Here's a complete working strategy example:

```python
import ttsprototyper as ttsp
import pandas as pd
import logging
import uuid


class SampleStrategy(ttsp.TTSPrototyper):
    """Sample dual moving average crossover strategy."""

    def calculate_indicators(self) -> pd.DataFrame:
        """Calculate technical indicators."""
        # 20-period Simple Moving Average (overlay on price chart)
        self._market_data_df["I00_sma_20"] = (
            self._market_data_df["close"].rolling(20).mean()
        )

        # 50-period Simple Moving Average (overlay on price chart)
        self._market_data_df["I00_sma_50"] = (
            self._market_data_df["close"].rolling(50).mean()
        )

        # RSI indicator (subplot 1)
        self._market_data_df["I01_rsi"] = self._calculate_rsi(
            self._market_data_df["close"], 14
        )

        return self._market_data_df

    def generate_signals(self) -> pd.DataFrame:
        """Generate trading signals."""
        # Long entry: Fast MA crosses above slow MA
        self._market_data_df["S00_long_entry"] = 0
        long_condition = (
            (self._market_data_df["I00_sma_20"] > self._market_data_df["I00_sma_50"]) &
            (self._market_data_df["I00_sma_20"].shift(1) <= self._market_data_df["I00_sma_50"].shift(1))
        )
        self._market_data_df.loc[long_condition, "S00_long_entry"] = 1

        # Exit signal: Fast MA crosses below slow MA
        self._market_data_df["S08_exit"] = 0
        exit_condition = (
            (self._market_data_df["I00_sma_20"] < self._market_data_df["I00_sma_50"]) &
            (self._market_data_df["I00_sma_20"].shift(1) >= self._market_data_df["I00_sma_50"].shift(1))
        )
        self._market_data_df.loc[exit_condition, "S08_exit"] = 1

        return self._market_data_df

    def apply_strategy_rules(self, row):
        """Apply trading logic."""
        current_position = self.get_current_position()

        # Enter long position
        if row.S00_long_entry == 1 and current_position == 0:
            order = ttsp.MarketOrder(
                order_id=uuid.uuid4(),
                ts_event=row.ts_event,
                order_direction=ttsp.Side.BUY,
                quantity=1.0
            )
            self.submit_order(order)

        # Exit position
        elif row.S08_exit == 1 and current_position > 0:
            order = ttsp.MarketOrder(
                order_id=uuid.uuid4(),
                ts_event=row.ts_event,
                order_direction=ttsp.Side.SELL,
                quantity=abs(current_position)
            )
            self.submit_order(order)

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))


def main():
    # Initialize strategy
    strategy = SampleStrategy(
        path_to_csv="data/market_data.csv",
        filter_for_symbol="MNQ",
        max_bars=5000,
        log_level=logging.INFO
    )

    # Set contract specifications (MNQ futures example)
    strategy.set_contract_specifications(
        point_value=2.0,
        tick_size=0.25,
        broker_commission_per_contract=0.25,
        exchange_fees_per_contract=0.37,
        minimum_fees=0.0
    )

    # Run backtest
    strategy.run()

    # Print results
    strategy.print_backtest_results(
        strategy_name="Sample MA Crossover",
        contract_name="MNQ"
    )

    # Generate charts and analysis
    strategy.generate_trade_charts(lookback_bars=50, lookforward_bars=50)

    print("\nBacktest complete! Check the 'backtest' folder for charts and analysis.")


if __name__ == "__main__":
    main()
```

### Google Colab Example

For Google Colab users, here's a complete example with proper setup:

```python
# Install and setup for Google Colab
!pip install ttsprototyper

# Mount Google Drive for persistent storage
from google.colab import drive
drive.mount('/content/drive')

# Change to Google Drive directory for persistent file storage
import os
os.chdir('/content/drive/MyDrive/trading_analysis')  # Create this folder in your Drive

# Upload your CSV file to Google Drive and update the path
import ttsprototyper as ttsp
import pandas as pd
import logging
import uuid

# Your strategy implementation (same as above)
class SampleStrategy(ttsp.TTSPrototyper):
    # ... (same implementation as above)
    pass

# Run the strategy
def main():
    strategy = SampleStrategy(
        path_to_csv="/content/drive/MyDrive/data/your_data.csv",  # Update path
        filter_for_symbol="MNQ",
        max_bars=1000,
        log_level=logging.INFO
    )

    strategy.set_contract_specifications(
        point_value=2.0,
        tick_size=0.25,
        broker_commission_per_contract=0.25,
        exchange_fees_per_contract=0.37,
        minimum_fees=0.0
    )

    strategy.run()
    strategy.print_backtest_results("Sample Strategy", "MNQ")
    strategy.generate_trade_charts(lookback_bars=50, lookforward_bars=50)

    print("Charts saved to Google Drive in 'backtest' folder!")
    print("You can download them or view them directly in Colab.")

main()
```

## Advanced Features

### Maximum Adverse/Favorable Excursion (MAE/MFE)
The prototyper automatically tracks MAE and MFE for every trade:

- **MAE**: Maximum unrealized loss during the trade (risk analysis)
- **MFE**: Maximum unrealized profit during the trade (opportunity analysis)
- **Winning Trade MAE**: Shows optimal stop-loss levels based on how much winning trades went against you
- **Points-based Measurement**: All values expressed in points for consistency across different instruments

### Equity Curve Analysis
Comprehensive equity curve generation with:
- **Multiple P&L Lines**: Net (after commissions) and gross (before commissions)
- **Drawdown Analysis**: Visual representation of underwater periods
- **Performance Statistics**: Embedded summary with key metrics
- **High-resolution Output**: 300 DPI charts suitable for reports

### Trade Journey Visualization
Unique visualization showing the "journey" of each trade:
- **Entry-relative Movements**: All movements calculated from entry price perspective
- **Maximum Excursions**: True maximum up/down movements during trade life
- **Exit Points**: Final realized P&L in points
- **Pattern Recognition**: Visual identification of trade development patterns

### Automatic Best/Worst Trade Organization
The prototyper automatically identifies and organizes:
- **Biggest Winners**: Top 25% or top 10 trades (whichever is smaller)
- **Biggest Losers**: Bottom 25% or bottom 10 trades (whichever is smaller)
- **Separate Folders**: Easy access to extreme performance examples
- **Descriptive Filenames**: Include trade number and P&L for quick identification

### Performance Statistics
Comprehensive statistics including:
- **Profit Factor**: Ratio of gross profit to gross loss
- **Risk-Reward Ratio**: Average winner to average loser ratio
- **Consecutive Trade Analysis**: Maximum consecutive wins and losses
- **Trade Duration Analysis**: Average holding time in minutes
- **Commission Impact**: Separate tracking of gross vs net performance

## Trading Hours & Restrictions

Trading time restrictions should be implemented at the signal or strategy level within your `generate_signals()` or `apply_strategy_rules()` methods:

```python
def generate_signals(self) -> pd.DataFrame:
    """Generate signals with trading hour restrictions."""
    # Convert timestamp to datetime for time filtering
    dt_series = pd.to_datetime(self._market_data_df['ts_event'])
    self._market_data_df['hour'] = dt_series.dt.hour
    self._market_data_df['minute'] = dt_series.dt.minute

    # Example: Only trade during regular hours (9:30 AM - 4:00 PM ET)
    regular_hours = (
        ((self._market_data_df['hour'] == 9) & (self._market_data_df['minute'] >= 30)) |  # 9:30 AM onwards
        ((self._market_data_df['hour'] > 9) & (self._market_data_df['hour'] < 16)) |      # 10 AM - 3:59 PM
        ((self._market_data_df['hour'] == 16) & (self._market_data_df['minute'] == 0))    # Exactly 4:00 PM
    )

    # Apply your signal logic (example: simple price above MA)
    base_signal = (
        self._market_data_df["close"] > self._market_data_df["I00_sma_20"]
    )

    # Restrict signals to trading hours
    self._market_data_df["S00_long_entry"] = 0
    self._market_data_df.loc[
        base_signal & regular_hours, "S00_long_entry"
    ] = 1

    return self._market_data_df
```

For MNQ futures contracts, you might restrict to regular trading hours:
```python
# MNQ regular trading hours (9:30 AM - 4:00 PM ET)
dt_series = pd.to_datetime(self._market_data_df['ts_event'])
hour = dt_series.dt.hour
minute = dt_series.dt.minute

regular_hours = (
    ((hour == 9) & (minute >= 30)) |  # 9:30 AM onwards
    ((hour > 9) & (hour < 16)) |      # 10 AM - 3:59 PM
    ((hour == 16) & (minute == 0))    # Exactly 4:00 PM
)
```

## Dependencies

The prototyper requires Python 3.11+ and the following packages:

### Core Dependencies
- **pandas (>=2.3.0,<3.0.0)**: Data manipulation and analysis
- **matplotlib (>=3.7.0,<4.0.0)**: Chart generation and visualization
- **rich (>=14.0.0,<15.0.0)**: Enhanced console output and progress bars

### Installation
```bash
# Install from PyPI
pip install ttsprototyper

# Or install with poetry for development
poetry install
```

### Development Dependencies
- **black**: Code formatting
- **poetry**: Dependency management and packaging

---

## Getting Started

1. **Install the package**: `pip install ttsprototyper`
2. **Prepare your data**: CSV file in Databento format with OHLCV data
3. **Create your strategy**: Subclass `TTSPrototyper` and implement the three required methods
4. **Set contract specifications**: Define point value, tick size, and commission structure
5. **Run your backtest**: Call `run()` to execute the strategy
6. **Analyze results**: Use `print_backtest_results()` and `generate_trade_charts()`
7. **Review charts**: Check the `backtest/` folder for detailed visual analysis

The prototyper is designed to keep you in the visual workflow that defines technical analysis - every trade can be charted and analyzed to refine your strategy based on actual market behavior.


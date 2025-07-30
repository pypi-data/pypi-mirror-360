"""Core trading strategy prototyping and backtesting framework.

This module provides the main TTSPrototyper class for building and testing
trading strategies. It handles market data loading, order execution simulation,
position management, and performance tracking.

Example:
    Basic usage of the TTSPrototyper:

    ```python
    class MyStrategy(TTSPrototyper):
        def calculate_indicators(self):
            # Add your indicators here
            pass

        def generate_signals(self):
            # Generate trading signals here
            pass

        def apply_strategy_rules(self, row):
            # Apply your strategy logic here
            pass

    strategy = MyStrategy("data.csv")
    strategy.set_contract_specifications(...)
    strategy.run()
    ```
"""

import abc
import logging
import os
import uuid
import pandas as pd
from collections import deque
from rich.progress import Progress, BarColumn, TimeElapsedColumn, TaskProgressColumn
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

from .ontology import (
    RecordType,
    OrderType,
    Side,
    OrderBase,
    MarketOrder,
    LimitOrder,
    StopOrder,
    Position,
    OrderFill,
    OrderCancellation,
    Trade,
    Contract,
    BacktestStatistics,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)



class TTSPrototyper(abc.ABC):
    """Abstract base class for trading strategy prototyping and backtesting.

    This class provides the framework for loading market data, processing orders,
    managing positions, and running backtests. Users must implement the abstract
    methods to define their specific trading strategy.

    The class handles:
        - Loading and validating market data from CSV files
        - Managing order execution and position tracking
        - Calculating commissions and fees
        - Providing hooks for custom strategy implementation

    Attributes:
        pending_market_orders: Dictionary of pending market orders by order ID
        pending_limit_orders: Dictionary of pending limit orders by order ID
        pending_stop_orders: Dictionary of pending stop orders by order ID
    """

    # =============================================================================
    # INITIALIZATION & CONFIGURATION
    # =============================================================================

    def __init__(
        self,
        path_to_csv: str,
        filter_for_symbol: str = None,
        max_bars: int = None,
        log_level: int = logging.INFO,
    ):
        """Initialize the TTS Prototyper with market data and configuration.

        Args:
            path_to_csv: Path to the CSV file containing market data
            filter_for_symbol: Optional symbol to filter data for
            max_bars: Optional limit on number of bars to load
            log_level: Logging level for the prototyper
        """
        logger.setLevel(log_level)

        # Store initialization parameters
        self._path_to_csv = path_to_csv
        self._filter_for_symbol = filter_for_symbol
        self._max_bars = max_bars

        # Initialize market data storage
        self._market_data_df = pd.DataFrame()

        # Initialize order fill tracking - buffer for performance, DataFrame for analysis
        self._fills_buffer = []  # Temporary buffer for batching fills
        self._fills_df = pd.DataFrame(  # Main fills storage for analysis
            columns=[
                "fill_id",
                "ts_event",
                "associated_order_id",
                "trade_direction",
                "quantity",
                "fill_at",
                "commission_and_fees",
                "fill_adjusted_for_commission_and_fees",
            ]
        )

        # Initialize order cancellation tracking
        self._cancellations_buffer = []  # Temporary buffer for batching cancellations
        self._cancellations_df = pd.DataFrame(  # Main cancellations storage for analysis
            columns=[
                "cancellation_id",
                "ts_event",
                "cancelled_order_id",
                "order_type",
                "cancellation_reason",
                "original_order",
            ]
        )

        # Initialize trading state
        self._contract_specifications = None  # Set via set_contract_specifications()
        self._positions = deque()  # FIFO queue for position tracking
        self._trade_stats = BacktestStatistics()  # Performance metrics

        # Trade tracking - from flat to flat
        self._current_trade: Trade = None  # Currently open trade (None when flat)
        self._completed_trades: list[Trade] = []  # List of completed trades
        self._trades_df = pd.DataFrame()  # DataFrame for trade analysis

        # Order management - separate dictionaries for each order type
        self.pending_market_orders: dict[uuid.UUID, MarketOrder] = {}
        self.pending_limit_orders: dict[uuid.UUID, LimitOrder] = {}
        self.pending_stop_orders: dict[uuid.UUID, StopOrder] = {}

        # Load and validate market data during initialization
        self._load_data()
        if self._market_data_df.empty:
            logger.warning(
                f"No data was loaded during initialization. "
                f"Please check your CSV file and parameters."
            )

    def _load_data(self):
        """Load and validate market data from CSV file.

        This method loads market data from the specified CSV file, applies filtering
        and validation, converts data types, and checks for data gaps. The loaded
        data is stored in self._market_data_df.

        Raises:
            ValueError: If no data found for specified symbol, multiple symbols found
                       without filter, or multiple record types found
            Exception: If CSV file cannot be read or other data loading errors occur
        """
        try:
            # Load CSV with specific columns and data types for performance
            # Note: Prices are stored as integers (in nano units) for precision
            self._market_data_df = pd.read_csv(
                self._path_to_csv,
                usecols=[
                    "ts_event",    # Timestamp in nanoseconds
                    "rtype",       # Record type (1s, 1m, 1h, 1d bars)
                    "open",        # OHLC prices in nano units
                    "high",
                    "low",
                    "close",
                    "volume",      # Volume
                    "symbol",      # Trading symbol
                ],
                dtype={
                    "ts_event": int,   # Large integers for nanosecond timestamps
                    "rtype": int,
                    "open": int,       # Integer prices for precision
                    "high": int,
                    "low": int,
                    "close": int,
                    "volume": int,
                    "symbol": str,
                },
            )

            # Apply symbol filtering if specified
            if self._filter_for_symbol is not None:
                self._market_data_df = self._market_data_df[
                    self._market_data_df["symbol"] == self._filter_for_symbol
                ]
                if self._market_data_df.empty:
                    raise ValueError(
                        f"No data found for symbol: {self._filter_for_symbol}"
                    )

            # Validate that we have data for only one symbol (required for backtesting)
            _unique_symbols = self._market_data_df["symbol"].unique()
            if len(_unique_symbols) > 1 and self._filter_for_symbol is None:
                raise ValueError(
                    f"Multiple symbols found in the data: {_unique_symbols.tolist()}. "
                    f"Please specify a symbol using filter_for_symbol parameter."
                )

            # Convert data types for proper handling
            # Convert nanosecond timestamps to pandas datetime objects
            self._market_data_df["ts_event"] = pd.to_datetime(
                self._market_data_df["ts_event"], unit="ns"
            )
            # Convert nano-unit prices to decimal prices (divide by 1 billion)
            self._market_data_df["open"] = self._market_data_df["open"] / 1e9
            self._market_data_df["high"] = self._market_data_df["high"] / 1e9
            self._market_data_df["low"] = self._market_data_df["low"] / 1e9
            self._market_data_df["close"] = self._market_data_df["close"] / 1e9

            # Apply max_bars limit if specified (useful for testing/development)
            if self._max_bars is not None and self._max_bars > 0:
                self._market_data_df = self._market_data_df.head(self._max_bars)
                logger.info(f"Limited data to first {self._max_bars} bars as requested")

            # Validate that all data is of the same time frame (record type)
            _rtypes = self._market_data_df["rtype"].unique().tolist()
            if len(_rtypes) != 1:
                raise ValueError(f"Expected single rtype but found multiple: {_rtypes}")

            _rtype = _rtypes[0]

            # Determine expected time difference between bars based on record type
            # This is used for gap detection in the data
            _expected_diff = None
            if _rtype == RecordType.OHLCV_1S.value:
                _expected_diff = pd.Timedelta("1S")
            elif _rtype == RecordType.OHLCV_1M.value:
                _expected_diff = pd.Timedelta("1min")
            elif _rtype == RecordType.OHLCV_1H.value:
                _expected_diff = pd.Timedelta("1H")
            elif _rtype == RecordType.OHLCV_1D.value:
                _expected_diff = pd.Timedelta("1D")

            # Perform gap detection and analysis
            if _expected_diff:
                # Sort data by timestamp to ensure chronological order
                self._market_data_df = self._market_data_df.sort_values("ts_event")

                # Calculate time differences between consecutive bars
                _time_diffs = self._market_data_df["ts_event"].diff()

                # Identify gaps (time differences larger than expected)
                _gaps = _time_diffs[_time_diffs > _expected_diff]

                if not _gaps.empty:
                    # Calculate gap statistics for reporting
                    _gap_count = len(_gaps)
                    _total_bars = len(self._market_data_df)
                    _gap_percent = (_gap_count / _total_bars) * 100

                    # Generate list of missing timestamps for detailed reporting
                    _missing_timestamps = []
                    for idx, diff in _gaps.items():
                        # Find the position in the current dataframe
                        df_position = self._market_data_df.index.get_loc(idx)
                        if df_position < len(self._market_data_df):
                            current_ts = self._market_data_df["ts_event"].iloc[df_position]
                            previous_ts = current_ts - diff
                            expected_ts = previous_ts + _expected_diff
                            # Calculate all missing timestamps in this gap
                            while expected_ts < current_ts:
                                _missing_timestamps.append(expected_ts)
                                expected_ts += _expected_diff

                    _missing_examples = [
                        ts.strftime("%Y-%m-%d %H:%M:%S")
                        for ts in _missing_timestamps[:3]
                    ]

                    logger.warning(
                        f"Found {_gap_count} gaps ({_gap_percent:.2f}%) in the data. "
                        f"Missing timestamps (first 3): {', '.join(_missing_examples)}"
                    )

            logger.info(
                f"Loaded {len(self._market_data_df)} "
                f"{RecordType.to_string(_rtypes[0])}, "
                f"time period: "
                f"{self._market_data_df['ts_event'].min()} to "
                f"{self._market_data_df['ts_event'].max()}."
            )
            logger.debug(
                f"Loaded market data to _market_data_df dataframe:\n"
                f"Note: The dataframe index might not correspond to the number set by "
                f"max_bars because a symbol filter was applied to exclude rows not "
                f"belonging to the requested symbol!\n{self._market_data_df}"
            )

        except Exception as e:
            logger.error(f"Error loading CSV file: {str(e)}")
            self._market_data_df = pd.DataFrame()
            raise e

    def set_contract_specifications(
        self,
        point_value: float,
        tick_size: float,
        broker_commission_per_contract: float,
        exchange_fees_per_contract: float,
        minimum_fees: float = 0.0,
        symbol: str = None,
    ) -> None:
        """Set contract specifications for trading calculations.

        This method configures the contract specifications needed for accurate
        profit/loss calculations, commission handling, and order execution.

        Args:
            point_value: Dollar value of one point move in the contract
            tick_size: Minimum price increment for the contract
            broker_commission_per_contract: Commission charged by broker per contract
            exchange_fees_per_contract: Fees charged by exchange per contract
            minimum_fees: Minimum fee amount (default: 0.0)
            symbol: Contract symbol (auto-detected from data if None)

        Raises:
            ValueError: If no market data loaded and symbol cannot be determined
        """
        # Auto-detect symbol from loaded data if not provided
        if symbol is None:
            if self._market_data_df.empty:
                raise ValueError("No market data loaded. Cannot determine symbol.")
            symbol = self._market_data_df["symbol"].iloc[0]

        # Create immutable contract specification object
        # This will auto-calculate total fees in both currency and point terms
        contract = Contract(
            symbol=symbol,
            point_value=point_value,
            tick_size=tick_size,
            broker_commission_per_contract=broker_commission_per_contract,
            exchange_fees_per_contract=exchange_fees_per_contract,
            minimum_fees=minimum_fees,
        )
        self._contract_specifications = contract

    # =============================================================================
    # ABSTRACT STRATEGY INTERFACE (must be implemented by subclasses)
    # =============================================================================

    @abc.abstractmethod
    def calculate_indicators(self) -> pd.DataFrame:
        """Calculate technical indicators and add them to the market data.

        This method should modify self._market_data_df to add indicator columns.

        Returns:
            pd.DataFrame: The market data with indicators added
        """
        pass

    @abc.abstractmethod
    def generate_signals(self) -> pd.DataFrame:
        """Generate trading signals based on indicators.

        This method should add signal columns to self._market_data_df.

        Returns:
            pd.DataFrame: The market data with signals added
        """
        pass

    @abc.abstractmethod
    def apply_strategy_rules(self, row):
        """Apply strategy rules for the current bar and submit orders if needed.

        This method is called for each bar during backtesting. It should analyze
        the current market conditions and submit orders using submit_order().

        Args:
            row: Current bar data (pandas Series-like object)
        """
        pass

    # =============================================================================
    # MAIN EXECUTION
    # =============================================================================

    def run(self):
        """Execute the complete backtesting workflow.

        This method orchestrates the entire backtesting process:
        1. Validates contract specifications are set
        2. Calculates indicators
        3. Generates signals
        4. Processes each bar and applies strategy rules
        5. Tracks positions and performance
        """
        try:
            # Validate that contract specifications have been set
            if self._contract_specifications is None:
                raise ValueError(
                    f"Contract specifications not set. Call "
                    f"set_contract_specifications() method before calling run() method."
                )

            # Execute the strategy preparation steps
            self.calculate_indicators()  # User-defined indicator calculations
            self.generate_signals()      # User-defined signal generation

            # Initialize columns for tracking position and break-even during backtest
            # These will be populated as the backtest progresses
            self._market_data_df["position"] = 0      # Net position at each bar
            self._market_data_df["break_even"] = None # Break-even price when in position

            with pd.option_context(
                # Setting the max_rows to 201 can show the first value of a 200 SMA
                "display.max_rows",
                201,
                "display.max_columns",
                None,
                "display.width",
                1000,
            ):
                logger.debug(
                    f"\n{self._market_data_df.head(201)}\n..."
                    f"\n{self._market_data_df.tail(100)}"
                )

            # Set up progress bar for backtesting visualization
            total_bars = len(self._market_data_df)
            bar_description = f"Processing {total_bars} bars..."

            with Progress(
                "[progress.description]{task.description}",
                BarColumn(),
                TaskProgressColumn(),
                "•",
                TimeElapsedColumn(),
            ) as progress:
                task = progress.add_task(bar_description, total=total_bars)

                # Main backtesting loop - process each bar chronologically
                for i, row in enumerate(self._market_data_df.itertuples()):
                    # Step 1: Process any pending orders from previous bars
                    self._process_pending_orders(row)

                    # Step 2: Apply user-defined strategy rules for this bar
                    self.apply_strategy_rules(row)

                    # Step 3: Update trade tracking with current market price
                    # Update unrealized P&L for open trades using the close price
                    if self._current_trade:
                        self._update_unrealized_pnl(row.close)

                    # Step 4: Record position state for analysis/charting
                    # Store the current net position after processing this bar
                    self._market_data_df.loc[
                        self._market_data_df.index[i], "position"
                    ] = self.get_current_position()

                    # Store the current break-even price if we have a position
                    if self.get_current_position() != 0:
                        self._market_data_df.loc[
                            self._market_data_df.index[i], "break_even"
                        ] = self.get_average_adjusted_entry_price()

                    # Update progress bar for user feedback
                    progress.update(task, advance=1)

            # Flush any remaining fills and cancellations from buffers
            self._flush_fills_buffer()
            self._flush_cancellations_buffer()

            # Close any open trade at the end of backtest for analysis
            self._close_open_trade_at_end()

            # Optionally generate trade charts automatically
            # Uncomment the next line to auto-generate charts after each backtest
            # self.generate_trade_charts()

        except Exception as e:
            logger.error(f"Error running strategy prototyper: {str(e)}")
            raise e

    # =============================================================================
    # PUBLIC QUERY METHODS
    # =============================================================================

    def get_current_position(self) -> float:
        """Get the current net position (positive = long, negative = short).

        Returns:
            float: Net position size (long quantity - short quantity)
        """
        # Calculate total long and short quantities separately
        long_quantity = sum(
            p.quantity for p in self._positions if p.direction == Side.BUY
        )
        short_quantity = sum(
            p.quantity for p in self._positions if p.direction == Side.SELL
        )
        # Return net position: positive = long, negative = short, zero = flat
        return long_quantity - short_quantity

    def get_average_adjusted_entry_price(self) -> float:
        """Calculate the average commission-adjusted entry price of current open positions.

        Returns:
            float: The weighted average commission-adjusted entry price of current positions.
                   Returns 0.0 if there are no open positions.
        """
        if not self._positions:
            return 0.0

        # Calculate weighted average of commission-adjusted entry prices
        # Note: All positions in the queue will be of the same direction due to FIFO closing
        total_value = sum(p.adjusted_entry_price * p.quantity for p in self._positions)
        total_quantity = sum(p.quantity for p in self._positions)

        return total_value / total_quantity if total_quantity > 0 else 0.0

    def get_current_trade(self) -> Trade:
        """Get the currently open trade.

        Returns:
            Trade: Current open trade, or None if position is flat
        """
        return self._current_trade

    def get_completed_trades(self) -> list[Trade]:
        """Get list of all completed trades.

        Returns:
            list[Trade]: List of completed trades from flat to flat
        """
        return self._completed_trades.copy()

    def get_trade_count(self) -> dict[str, int]:
        """Get trade statistics.

        Returns:
            dict: Dictionary with trade counts (total, winning, losing, open)
        """
        winning = sum(1 for trade in self._completed_trades if trade.realized_pnl > 0)
        losing = sum(1 for trade in self._completed_trades if trade.realized_pnl < 0)

        return {
            "total_completed": len(self._completed_trades),
            "winning": winning,
            "losing": losing,
            "open": 1 if self._current_trade else 0,
        }

    def get_trades_dataframe(self) -> pd.DataFrame:
        """Get trades as a pandas DataFrame for analysis.

        Returns:
            pd.DataFrame: DataFrame containing all completed trades
        """
        if not self._completed_trades:
            return pd.DataFrame()

        # Convert completed trades to DataFrame
        trades_data = []
        for trade in self._completed_trades:
            trades_data.append({
                'trade_id': trade.trade_id,
                'entry_time': trade.entry_time,
                'exit_time': trade.exit_time,
                'direction': trade.direction.value,
                'max_quantity': trade.max_quantity,
                'realized_pnl': trade.realized_pnl,
                'total_commission': trade.total_commission,
                'duration': trade.duration,
                'weighted_avg_entry_price': trade.weighted_avg_entry_price,
                'weighted_avg_exit_price': trade.weighted_avg_exit_price,
                'entry_fills_count': len(trade.entry_fills),
                'exit_fills_count': len(trade.exit_fills),
                'max_adverse_excursion': trade.max_adverse_excursion,
                'max_favorable_excursion': trade.max_favorable_excursion,
            })

        return pd.DataFrame(trades_data)

    def generate_trade_charts(self, lookback_bars: int = 50, lookforward_bars: int = 50) -> None:
        """Generate individual charts for each completed trade.

        Creates a 'backtest/trade_charts' directory with one PNG file per trade,
        showing price action, indicators, fills, P&L tracking, and trade statistics.

        Args:
            lookback_bars: Number of bars to show before trade entry
            lookforward_bars: Number of bars to show after trade exit
        """
        if not self._completed_trades:
            logger.info("No completed trades to chart")
            return

        # Clean up existing backtest folders before generating new charts
        self._cleanup_backtest_folders()

        # Create directory structure
        os.makedirs("backtest/trade_charts", exist_ok=True)
        os.makedirs("backtest/stats", exist_ok=True)

        total_trades = len(self._completed_trades)
        logger.info(f"Generating charts for {total_trades} completed trades")

        # Create progress bar for chart generation
        with Progress(
            "[progress.description]{task.description}",
            BarColumn(),
            TaskProgressColumn(),
            "•",
            TimeElapsedColumn(),
        ) as progress:
            chart_task = progress.add_task(
                f"Generating {total_trades} trade charts", total=total_trades
            )

            # Generate chart for each completed trade
            for i, trade in enumerate(self._completed_trades, 1):
                try:
                    self._create_individual_trade_chart(
                        trade, i, lookback_bars, lookforward_bars
                    )
                    progress.update(chart_task, advance=1)
                except Exception as e:
                    logger.error(f"Error generating chart for trade {i}: {str(e)}")
                    progress.update(chart_task, advance=1)

        logger.info(f"Generated {total_trades} trade charts in 'backtest/trade_charts' directory")

        # Copy biggest winners and losers to separate folders
        self._organize_best_worst_charts()

        # Generate equity curve chart
        self._generate_equity_curve_chart()

        # Generate MAE/MFE analysis chart
        self._generate_mae_mfe_chart()

        # Generate trade journey chart
        self._generate_trade_journey_chart()

    def print_backtest_results(self, strategy_name: str = "Strategy", contract_name: str = "Contract") -> None:
        """Print comprehensive backtest results in a formatted report.

        Args:
            strategy_name: Name of the strategy for the report header
            contract_name: Name of the contract/instrument traded
        """
        print("\n" + "=" * 60)
        print(f"{strategy_name.upper()} - BACKTEST RESULTS")
        print("=" * 60)

        # Trade statistics
        trade_stats = self.get_trade_count()
        print(f"\nTrade Statistics:")
        print(f"  Total Completed Trades: {trade_stats['total_completed']}")
        print(f"  Winning Trades: {trade_stats['winning']}")
        print(f"  Losing Trades: {trade_stats['losing']}")
        print(f"  Open Trades: {trade_stats['open']}")

        if trade_stats['total_completed'] > 0:
            win_rate = (trade_stats['winning'] / trade_stats['total_completed']) * 100
            print(f"  Win Rate: {win_rate:.1f}%")

        # P&L Analysis
        completed_trades = self.get_completed_trades()
        if completed_trades:
            # Calculate P&L metrics
            net_pnl = sum(trade.realized_pnl for trade in completed_trades)
            total_commission = sum(trade.total_commission for trade in completed_trades)
            gross_pnl = net_pnl + total_commission

            winning_trades = [t for t in completed_trades if t.realized_pnl > 0]
            losing_trades = [t for t in completed_trades if t.realized_pnl < 0]

            print(f"\nP&L Analysis:")
            print(f"  Gross P&L: ${gross_pnl:.2f}")
            print(f"  Total Commission: ${total_commission:.2f}")
            print(f"  Net P&L: ${net_pnl:.2f}")

            if winning_trades:
                avg_winner = sum(t.realized_pnl for t in winning_trades) / len(winning_trades)
                print(f"  Average Winner: ${avg_winner:.2f}")

            if losing_trades:
                avg_loser = sum(t.realized_pnl for t in losing_trades) / len(losing_trades)
                print(f"  Average Loser: ${avg_loser:.2f}")

            if winning_trades and losing_trades:
                profit_factor = abs(sum(t.realized_pnl for t in winning_trades) /
                                  sum(t.realized_pnl for t in losing_trades))
                print(f"  Profit Factor: {profit_factor:.2f}")

                # Calculate Risk Reward Ratio (Average Winner / Average Loser)
                avg_winner = sum(t.realized_pnl for t in winning_trades) / len(winning_trades)
                avg_loser = sum(t.realized_pnl for t in losing_trades) / len(losing_trades)
                risk_reward_ratio = avg_winner / abs(avg_loser)
                print(f"  Risk Reward Ratio: {risk_reward_ratio:.2f}")

            # Best and worst trades
            if completed_trades:
                best_trade = max(completed_trades, key=lambda t: t.realized_pnl)
                worst_trade = min(completed_trades, key=lambda t: t.realized_pnl)
                print(f"  Biggest Winner: ${best_trade.realized_pnl:.2f}")
                print(f"  Biggest Loser: ${worst_trade.realized_pnl:.2f}")

            # Additional metrics
            if completed_trades:
                avg_trade_duration = sum(
                    (t.duration.total_seconds() / 60 for t in completed_trades if t.duration), 0
                ) / len(completed_trades)
                print(f"  Average Trade Duration: {avg_trade_duration:.1f} minutes")

                # Consecutive wins/losses
                consecutive_wins, consecutive_losses = self._calculate_consecutive_trades(completed_trades)
                print(f"  Max Consecutive Wins: {consecutive_wins}")
                print(f"  Max Consecutive Losses: {consecutive_losses}")

                # Trade duration analysis
                durations = [t.duration.total_seconds() / 60 for t in completed_trades if t.duration]
                if durations:
                    shortest_trade = min(durations)
                    longest_trade = max(durations)
                    print(f"  Shortest Trade: {shortest_trade:.1f} minutes")
                    print(f"  Longest Trade: {longest_trade:.1f} minutes")

                # Drawdown analysis
                drawdown_info = self._calculate_drawdown_metrics(completed_trades)
                if drawdown_info:
                    print(f"  Maximum Drawdown: ${drawdown_info['max_drawdown']:.2f}")
                    print(f"  Drawdown Duration: {drawdown_info['drawdown_duration']:.1f} trades")

                max_position = self._trade_stats.max_position_size
                print(f"  Maximum Position Size: {max_position} contracts")

                # Trade distribution analysis
                print(f"\nTrade Distribution:")
                self._print_trade_distribution(completed_trades)

                # MAE/MFE Analysis
                print(f"\nMAE/MFE Analysis:")
                self._print_mae_mfe_analysis(completed_trades)

        # Current position
        current_trade = self.get_current_trade()
        if current_trade:
            print(f"\nCurrent Open Position:")
            print(f"  Direction: {current_trade.direction.value}")
            print(f"  Entry Time: {current_trade.entry_time}")
            print(f"  Entry Price: ${current_trade.weighted_avg_entry_price:.2f}")
            print(f"  Unrealized P&L: ${current_trade.unrealized_pnl:.2f}")
            print(f"  Current Quantity: {current_trade.max_quantity}")
        else:
            print(f"\nCurrent Position: FLAT")

        # Contract and data info
        if self._contract_specifications:
            print(f"\nContract Information:")
            print(f"  Symbol: {self._contract_specifications.symbol}")
            print(f"  Point Value: ${self._contract_specifications.point_value:.2f}")
            print(f"  Tick Size: {self._contract_specifications.tick_size}")
            print(f"  Commission per Contract: ${self._contract_specifications.broker_commission_per_contract:.2f}")
            print(f"  Exchange Fees per Contract: ${self._contract_specifications.exchange_fees_per_contract:.2f}")

        # Data summary
        if not self._market_data_df.empty:
            data_start = self._market_data_df['ts_event'].min()
            data_end = self._market_data_df['ts_event'].max()
            total_bars = len(self._market_data_df)
            print(f"\nData Summary:")
            print(f"  Period: {data_start} to {data_end}")
            print(f"  Total Bars: {total_bars:,}")

        print("\n" + "=" * 60)

    def _calculate_consecutive_trades(self, completed_trades: list) -> tuple[int, int]:
        """Calculate maximum consecutive wins and losses.

        Args:
            completed_trades: List of completed Trade objects

        Returns:
            tuple: (max_consecutive_wins, max_consecutive_losses)
        """
        if not completed_trades:
            return 0, 0

        max_wins = 0
        max_losses = 0
        current_wins = 0
        current_losses = 0

        for trade in completed_trades:
            if trade.realized_pnl > 0:
                # Winning trade
                current_wins += 1
                current_losses = 0
                max_wins = max(max_wins, current_wins)
            elif trade.realized_pnl < 0:
                # Losing trade
                current_losses += 1
                current_wins = 0
                max_losses = max(max_losses, current_losses)
            else:
                # Break-even trade
                current_wins = 0
                current_losses = 0

        return max_wins, max_losses

    def _organize_best_worst_charts(self) -> None:
        """Copy charts of biggest winners and losers to separate folders."""
        import shutil
        import os

        completed_trades = self.get_completed_trades()
        if not completed_trades:
            return

        # Create directories
        winners_dir = "backtest/biggest_winners"
        losers_dir = "backtest/biggest_losers"
        os.makedirs(winners_dir, exist_ok=True)
        os.makedirs(losers_dir, exist_ok=True)

        # Sort trades by P&L
        sorted_trades = sorted(completed_trades, key=lambda t: t.realized_pnl, reverse=True)

        # Get top 10 winners and losers (or fewer if less than 10 trades)
        num_to_copy = min(10, len(sorted_trades) // 4)  # Copy top 25% or 10, whichever is smaller
        if num_to_copy < 1:
            num_to_copy = 1

        biggest_winners = sorted_trades[:num_to_copy]
        biggest_losers = sorted_trades[-num_to_copy:]

        # Copy winner charts
        for i, trade in enumerate(biggest_winners, 1):
            trade_num = self._get_trade_number(trade)
            if trade_num is not None:
                source_path = f"backtest/trade_charts/trade_{trade_num:03d}.png"
                dest_path = f"{winners_dir}/winner_{i:02d}_trade_{trade_num:03d}_pnl_{trade.realized_pnl:.2f}.png"

                if os.path.exists(source_path):
                    shutil.copy2(source_path, dest_path)

        # Copy loser charts
        for i, trade in enumerate(biggest_losers, 1):
            trade_num = self._get_trade_number(trade)
            if trade_num is not None:
                source_path = f"backtest/trade_charts/trade_{trade_num:03d}.png"
                dest_path = f"{losers_dir}/loser_{i:02d}_trade_{trade_num:03d}_pnl_{trade.realized_pnl:.2f}.png"

                if os.path.exists(source_path):
                    shutil.copy2(source_path, dest_path)

        logger.info(f"Copied {len(biggest_winners)} biggest winner charts to '{winners_dir}'")
        logger.info(f"Copied {len(biggest_losers)} biggest loser charts to '{losers_dir}'")

    def _generate_equity_curve_chart(self) -> None:
        """Generate comprehensive equity curve chart with P&L and drawdown analysis."""
        if not self._completed_trades:
            logger.warning("No completed trades found. Cannot generate equity curve.")
            return

        # Calculate equity curve data
        equity_data = self._calculate_equity_curve_data()

        if not equity_data:
            logger.warning("No equity data available for chart generation.")
            return

        # Create the equity curve chart
        self._create_equity_curve_plot(equity_data)

        logger.info("Generated equity curve chart in 'backtest/stats/equity_curve.png'")

    def _calculate_equity_curve_data(self) -> dict:
        """Calculate equity curve data including running P&L, drawdown, and statistics."""
        trades = self._completed_trades
        if not trades:
            return {}

        # Initialize data structures
        trade_numbers = []
        trade_dates = []
        running_pnl = []
        running_gross_pnl = []
        drawdown = []
        underwater_curve = []

        # Running calculations
        current_pnl = 0.0
        current_gross_pnl = 0.0
        peak_pnl = 0.0
        peak_gross_pnl = 0.0

        for i, trade in enumerate(trades, 1):
            # Update running P&L
            current_pnl += trade.realized_pnl
            current_gross_pnl += (trade.realized_pnl + trade.total_commission)

            # Update peaks
            peak_pnl = max(peak_pnl, current_pnl)
            peak_gross_pnl = max(peak_gross_pnl, current_gross_pnl)

            # Calculate drawdowns
            current_drawdown = peak_pnl - current_pnl
            current_gross_drawdown = peak_gross_pnl - current_gross_pnl

            # Store data
            trade_numbers.append(i)
            trade_dates.append(trade.exit_time)
            running_pnl.append(current_pnl)
            running_gross_pnl.append(current_gross_pnl)
            drawdown.append(-current_drawdown)  # Negative for plotting below zero
            underwater_curve.append(-current_gross_drawdown)

        return {
            'trade_numbers': trade_numbers,
            'trade_dates': trade_dates,
            'running_pnl': running_pnl,
            'running_gross_pnl': running_gross_pnl,
            'drawdown': drawdown,
            'underwater_curve': underwater_curve,
            'final_pnl': current_pnl,
            'final_gross_pnl': current_gross_pnl,
            'max_drawdown': min(drawdown),
            'max_gross_drawdown': min(underwater_curve)
        }

    def _create_equity_curve_plot(self, equity_data: dict) -> None:
        """Create and save the equity curve chart."""
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from matplotlib.patches import Rectangle

        # Create figure with subplots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12),
                                           gridspec_kw={'height_ratios': [3, 2, 1]})

        # Plot 1: Equity Curves
        ax1.plot(equity_data['trade_numbers'], equity_data['running_pnl'],
                 label='Net P&L', linewidth=2, color='blue', alpha=0.8)
        ax1.plot(equity_data['trade_numbers'], equity_data['running_gross_pnl'],
                 label='Gross P&L', linewidth=1.5, color='lightblue', alpha=0.7)

        # Add zero line
        ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=0.8)

        # Highlight profitable and losing periods
        for i in range(len(equity_data['running_pnl'])):
            if equity_data['running_pnl'][i] > 0:
                ax1.axvspan(i, i+1, alpha=0.1, color='green')
            else:
                ax1.axvspan(i, i+1, alpha=0.1, color='red')

        ax1.set_title('Equity Curve - Strategy Performance Over Time', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Cumulative P&L ($)', fontsize=12)
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0)  # Transparent grid (change to 0.3 to make visible)

        # Plot 2: Drawdown
        ax2.fill_between(equity_data['trade_numbers'], equity_data['drawdown'], 0,
                        color='red', alpha=0.3, label='Net Drawdown')
        ax2.fill_between(equity_data['trade_numbers'], equity_data['underwater_curve'], 0,
                        color='orange', alpha=0.2, label='Gross Drawdown')
        ax2.plot(equity_data['trade_numbers'], equity_data['drawdown'],
                color='red', linewidth=1.5, alpha=0.8)
        ax2.plot(equity_data['trade_numbers'], equity_data['underwater_curve'],
                color='orange', linewidth=1, alpha=0.7)

        ax2.set_title('Drawdown Analysis', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Drawdown ($)', fontsize=12)
        ax2.legend(loc='lower right')
        ax2.grid(True, alpha=0)  # Transparent grid (change to 0.3 to make visible)

        # Plot 3: Trade P&L Distribution
        trade_pnls = [trade.realized_pnl for trade in self._completed_trades]
        colors = ['green' if pnl > 0 else 'red' for pnl in trade_pnls]

        ax3.bar(equity_data['trade_numbers'], trade_pnls, color=colors, alpha=0.6, width=0.8)
        ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=1)

        ax3.set_title('Individual Trade P&L', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Trade Number', fontsize=12)
        ax3.set_ylabel('Trade P&L ($)', fontsize=12)
        ax3.grid(True, alpha=0)  # Transparent grid (change to 0.3 to make visible)

        # Add summary statistics as text box
        stats_text = self._create_equity_curve_stats_text(equity_data)
        ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        # Adjust layout and save
        plt.tight_layout()
        plt.savefig('backtest/stats/equity_curve.png', dpi=300, bbox_inches='tight')
        plt.close()

    def _create_equity_curve_stats_text(self, equity_data: dict) -> str:
        """Create summary statistics text for equity curve chart."""
        trades = self._completed_trades
        winning_trades = [t for t in trades if t.realized_pnl > 0]
        losing_trades = [t for t in trades if t.realized_pnl < 0]

        # Calculate key metrics
        total_trades = len(trades)
        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0

        avg_winner = sum(t.realized_pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loser = sum(t.realized_pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0

        profit_factor = (abs(sum(t.realized_pnl for t in winning_trades)) /
                        abs(sum(t.realized_pnl for t in losing_trades))) if losing_trades else float('inf')

        risk_reward_ratio = avg_winner / abs(avg_loser) if avg_loser != 0 else float('inf')

        # Create formatted text
        stats_text = f"""Strategy Performance Summary
Total Trades: {total_trades}
Win Rate: {win_rate:.1f}%
Final P&L: ${equity_data['final_pnl']:.2f}
Max Drawdown: ${abs(equity_data['max_drawdown']):.2f}
Profit Factor: {profit_factor:.2f}
Risk/Reward: {risk_reward_ratio:.2f}"""

        return stats_text

    def _generate_mae_mfe_chart(self) -> None:
        """Generate MAE vs MFE scatter plot chart for trade analysis.

        Creates a scatter plot showing Maximum Adverse Excursion (MAE) vs
        Maximum Favorable Excursion (MFE) for each trade. This helps identify
        optimal stop-loss and take-profit levels.
        """
        if not self._completed_trades:
            logger.warning("No completed trades found. Cannot generate MAE/MFE chart.")
            return

        # Calculate MAE/MFE data
        mae_mfe_data = self._calculate_mae_mfe_data()

        if not mae_mfe_data:
            logger.warning("No MAE/MFE data available for chart generation.")
            return

        # Create the MAE/MFE chart
        self._create_mae_mfe_plot(mae_mfe_data)

        logger.info("Generated MAE/MFE analysis chart in 'backtest/stats/mae_mfe_analysis.png'")

    def _calculate_mae_mfe_data(self) -> dict:
        """Calculate MAE/MFE data for all completed trades."""
        trades = self._completed_trades
        if not trades:
            return {}

        # Get point value for conversion
        point_value = self._contract_specifications.point_value if self._contract_specifications else 1.0

        # Separate winning and losing trades
        winning_trades = [t for t in trades if t.realized_pnl > 0]
        losing_trades = [t for t in trades if t.realized_pnl < 0]
        breakeven_trades = [t for t in trades if t.realized_pnl == 0]

        # Extract MAE/MFE data in points
        mae_mfe_data = {
            'winning_trades': {
                'mae_points': [t.max_adverse_excursion / point_value for t in winning_trades],
                'mfe_points': [t.max_favorable_excursion / point_value for t in winning_trades],
                'pnl': [t.realized_pnl for t in winning_trades],
                'trade_numbers': [i+1 for i, t in enumerate(trades) if t.realized_pnl > 0]
            },
            'losing_trades': {
                'mae_points': [t.max_adverse_excursion / point_value for t in losing_trades],
                'mfe_points': [t.max_favorable_excursion / point_value for t in losing_trades],
                'pnl': [t.realized_pnl for t in losing_trades],
                'trade_numbers': [i+1 for i, t in enumerate(trades) if t.realized_pnl < 0]
            },
            'breakeven_trades': {
                'mae_points': [t.max_adverse_excursion / point_value for t in breakeven_trades],
                'mfe_points': [t.max_favorable_excursion / point_value for t in breakeven_trades],
                'pnl': [t.realized_pnl for t in breakeven_trades],
                'trade_numbers': [i+1 for i, t in enumerate(trades) if t.realized_pnl == 0]
            },
            'point_value': point_value,
            'total_trades': len(trades),
            'winning_count': len(winning_trades),
            'losing_count': len(losing_trades),
            'breakeven_count': len(breakeven_trades)
        }

        return mae_mfe_data

    def _create_mae_mfe_plot(self, mae_mfe_data: dict) -> None:
        """Create and save the MAE vs MFE scatter plot chart."""
        import matplotlib.pyplot as plt
        import numpy as np

        # Create figure
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))

        # Plot winning trades
        if mae_mfe_data['winning_trades']['mae_points']:
            scatter_wins = ax.scatter(
                mae_mfe_data['winning_trades']['mae_points'],
                mae_mfe_data['winning_trades']['mfe_points'],
                c='green', alpha=0.6, s=50, label=f"Winning Trades ({mae_mfe_data['winning_count']})",
                edgecolors='darkgreen', linewidth=0.5
            )

        # Plot losing trades
        if mae_mfe_data['losing_trades']['mae_points']:
            scatter_losses = ax.scatter(
                mae_mfe_data['losing_trades']['mae_points'],
                mae_mfe_data['losing_trades']['mfe_points'],
                c='red', alpha=0.6, s=50, label=f"Losing Trades ({mae_mfe_data['losing_count']})",
                edgecolors='darkred', linewidth=0.5
            )

        # Plot breakeven trades if any
        if mae_mfe_data['breakeven_trades']['mae_points']:
            scatter_breakeven = ax.scatter(
                mae_mfe_data['breakeven_trades']['mae_points'],
                mae_mfe_data['breakeven_trades']['mfe_points'],
                c='gray', alpha=0.6, s=50, label=f"Breakeven Trades ({mae_mfe_data['breakeven_count']})",
                edgecolors='black', linewidth=0.5
            )

        # Calculate and plot trend lines and statistics
        self._add_mae_mfe_analysis_lines(ax, mae_mfe_data)

        # Formatting
        ax.set_xlabel('Maximum Adverse Excursion (MAE) - Points', fontsize=12)
        ax.set_ylabel('Maximum Favorable Excursion (MFE) - Points', fontsize=12)
        ax.set_title('MAE vs MFE Analysis - Trade Risk/Reward Profile', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0)  # Transparent grid (change to 0.3 to make visible)
        ax.legend(loc='upper right')

        # Add statistics text box
        stats_text = self._create_mae_mfe_stats_text(mae_mfe_data)
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

        # Set axis limits with some padding
        all_mae = (mae_mfe_data['winning_trades']['mae_points'] +
                  mae_mfe_data['losing_trades']['mae_points'] +
                  mae_mfe_data['breakeven_trades']['mae_points'])
        all_mfe = (mae_mfe_data['winning_trades']['mfe_points'] +
                  mae_mfe_data['losing_trades']['mfe_points'] +
                  mae_mfe_data['breakeven_trades']['mfe_points'])

        if all_mae and all_mfe:
            mae_max = max(all_mae) * 1.1
            mfe_max = max(all_mfe) * 1.1
            ax.set_xlim(0, mae_max)
            ax.set_ylim(0, mfe_max)

        # Save the chart
        plt.tight_layout()
        plt.savefig('backtest/stats/mae_mfe_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()

    def _add_mae_mfe_analysis_lines(self, ax, mae_mfe_data: dict) -> None:
        """Add analysis lines and zones to the MAE/MFE chart."""
        import numpy as np

        # Calculate percentiles for winning trades MAE (for stop-loss optimization)
        winning_mae = mae_mfe_data['winning_trades']['mae_points']
        if winning_mae:
            mae_90th = np.percentile(winning_mae, 90)
            mae_95th = np.percentile(winning_mae, 95)

            # Add vertical lines for stop-loss levels
            ax.axvline(x=mae_90th, color='orange', linestyle='--', alpha=0.7,
                      label=f'90th Percentile MAE: {mae_90th:.1f} pts')
            ax.axvline(x=mae_95th, color='red', linestyle='--', alpha=0.7,
                      label=f'95th Percentile MAE: {mae_95th:.1f} pts')

        # Calculate percentiles for MFE (for take-profit optimization)
        all_mfe = (mae_mfe_data['winning_trades']['mfe_points'] +
                  mae_mfe_data['losing_trades']['mfe_points'])
        if all_mfe:
            mfe_50th = np.percentile(all_mfe, 50)
            mfe_75th = np.percentile(all_mfe, 75)

            # Add horizontal lines for take-profit levels
            ax.axhline(y=mfe_50th, color='lightgreen', linestyle=':', alpha=0.7,
                      label=f'50th Percentile MFE: {mfe_50th:.1f} pts')
            ax.axhline(y=mfe_75th, color='green', linestyle=':', alpha=0.7,
                      label=f'75th Percentile MFE: {mfe_75th:.1f} pts')

    def _create_mae_mfe_stats_text(self, mae_mfe_data: dict) -> str:
        """Create summary statistics text for MAE/MFE chart."""
        import numpy as np

        winning_mae = mae_mfe_data['winning_trades']['mae_points']
        losing_mae = mae_mfe_data['losing_trades']['mae_points']
        winning_mfe = mae_mfe_data['winning_trades']['mfe_points']
        losing_mfe = mae_mfe_data['losing_trades']['mfe_points']

        stats_lines = ["MAE/MFE Analysis Summary"]
        stats_lines.append(f"Total Trades: {mae_mfe_data['total_trades']}")
        stats_lines.append("")

        # MAE Statistics for winning trades (key for stop-loss optimization)
        if winning_mae:
            avg_winning_mae = np.mean(winning_mae)
            max_winning_mae = np.max(winning_mae)
            mae_90th = np.percentile(winning_mae, 90)
            stats_lines.append("Winning Trades MAE:")
            stats_lines.append(f"  Average: {avg_winning_mae:.1f} pts")
            stats_lines.append(f"  Maximum: {max_winning_mae:.1f} pts")
            stats_lines.append(f"  90th %ile: {mae_90th:.1f} pts")
            stats_lines.append("")

        # MFE Statistics
        if winning_mfe:
            avg_winning_mfe = np.mean(winning_mfe)
            max_winning_mfe = np.max(winning_mfe)
            stats_lines.append("Winning Trades MFE:")
            stats_lines.append(f"  Average: {avg_winning_mfe:.1f} pts")
            stats_lines.append(f"  Maximum: {max_winning_mfe:.1f} pts")

        return "\n".join(stats_lines)

    def _generate_trade_journey_chart(self) -> None:
        """Generate trade journey chart showing max up/down movement and exit points.

        Creates a bar chart showing for each trade:
        - Maximum upward movement (MFE in points)
        - Maximum downward movement (MAE in points)
        - Final exit point (realized P&L in points)
        """
        if not self._completed_trades:
            logger.warning("No completed trades found. Cannot generate trade journey chart.")
            return

        # Calculate trade journey data
        journey_data = self._calculate_trade_journey_data()

        if not journey_data:
            logger.warning("No trade journey data available for chart generation.")
            return

        # Create the trade journey chart
        self._create_trade_journey_plot(journey_data)

        logger.info("Generated trade journey chart in 'backtest/stats/trade_journey.png'")

    def _calculate_trade_journey_data(self) -> dict:
        """Calculate trade journey data for all completed trades.

        For the trade journey chart, we calculate the absolute maximum positive
        and negative price movements from entry, which is different from MAE/MFE
        that are used for risk analysis.
        """
        trades = self._completed_trades
        if not trades:
            return {}

        # Get point value for conversion
        point_value = self._contract_specifications.point_value if self._contract_specifications else 1.0

        # Calculate true max up/down movements for each trade
        trade_numbers = list(range(1, len(trades) + 1))
        max_up_points = []
        max_down_points = []
        exit_points = []

        for trade in trades:
            # Calculate exit points (realized P&L in points)
            exit_pnl_points = trade.realized_pnl / point_value
            exit_points.append(exit_pnl_points)

            # Calculate true maximum movements from entry price
            max_up, max_down = self._calculate_true_max_movements(trade)
            max_up_points.append(max_up / point_value)
            max_down_points.append(-max_down / point_value)  # Negative for downward display

        # Separate winning and losing trades for color coding
        winning_trades = [i for i, t in enumerate(trades) if t.realized_pnl > 0]
        losing_trades = [i for i, t in enumerate(trades) if t.realized_pnl < 0]
        breakeven_trades = [i for i, t in enumerate(trades) if t.realized_pnl == 0]

        journey_data = {
            'trade_numbers': trade_numbers,
            'max_up_points': max_up_points,
            'max_down_points': max_down_points,
            'exit_points': exit_points,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'breakeven_trades': breakeven_trades,
            'point_value': point_value,
            'total_trades': len(trades)
        }

        return journey_data

    def _calculate_true_max_movements(self, trade) -> tuple:
        """Calculate the true maximum positive and negative price movements from entry.

        This analyzes the actual market data during the trade period to find
        the absolute highest and lowest points relative to the entry price.
        For the exit bar, uses the actual exit price as the limit, not the bar's high/low.

        Args:
            trade: Trade object to analyze

        Returns:
            tuple: (max_positive_movement, max_negative_movement) in currency units
        """
        if not trade.entry_time or not trade.exit_time:
            return (0.0, 0.0)

        # Get the market data for the trade period
        trade_data = self._market_data_df[
            (self._market_data_df['ts_event'] >= trade.entry_time) &
            (self._market_data_df['ts_event'] <= trade.exit_time)
        ].copy()

        if trade_data.empty:
            return (0.0, 0.0)

        # Get entry and exit prices
        entry_price = trade.weighted_avg_entry_price
        exit_price = trade.weighted_avg_exit_price
        if not entry_price or not exit_price:
            return (0.0, 0.0)

        # Separate the exit bar from the rest of the trade data
        exit_bar = trade_data[trade_data['ts_event'] == trade.exit_time]
        pre_exit_data = trade_data[trade_data['ts_event'] < trade.exit_time]

        # For pre-exit bars, use actual highs and lows
        if not pre_exit_data.empty:
            pre_exit_highest = pre_exit_data['high'].max()
            pre_exit_lowest = pre_exit_data['low'].min()
        else:
            pre_exit_highest = entry_price
            pre_exit_lowest = entry_price

        # For the exit bar, the trade only experiences movement up to the exit price
        # So we need to limit the high/low to the exit price
        if not exit_bar.empty:
            exit_bar_high = exit_bar['high'].iloc[0]
            exit_bar_low = exit_bar['low'].iloc[0]

            # The actual highest/lowest the trade experienced in the exit bar
            # is limited by the exit price
            if trade.direction.value == 'BUY':
                # For long trades, if exit price is below bar high, use exit price as max high
                # If exit price is above bar low, use exit price as max low
                actual_exit_bar_high = min(exit_bar_high, exit_price)
                actual_exit_bar_low = max(exit_bar_low, exit_price)
            else:
                # For short trades, similar logic but reversed
                actual_exit_bar_high = min(exit_bar_high, exit_price)
                actual_exit_bar_low = max(exit_bar_low, exit_price)

            # Combine pre-exit and exit bar extremes
            highest_price = max(pre_exit_highest, actual_exit_bar_high)
            lowest_price = min(pre_exit_lowest, actual_exit_bar_low)
        else:
            # No exit bar found, use pre-exit data only
            highest_price = pre_exit_highest
            lowest_price = pre_exit_lowest

        # Calculate movements from entry price
        if trade.direction.value == 'BUY':
            # Long trade: positive movement is price going up, negative is going down
            max_positive_movement = max(0, highest_price - entry_price)
            max_negative_movement = max(0, entry_price - lowest_price)
        else:
            # Short trade: positive movement is price going down, negative is going up
            max_positive_movement = max(0, entry_price - lowest_price)
            max_negative_movement = max(0, highest_price - entry_price)

        # Convert to currency using point value
        point_value = self._contract_specifications.point_value if self._contract_specifications else 1.0
        max_positive_currency = max_positive_movement * point_value
        max_negative_currency = max_negative_movement * point_value

        return (max_positive_currency, max_negative_currency)

    def _create_trade_journey_plot(self, journey_data: dict) -> None:
        """Create and save the trade journey chart."""
        import matplotlib.pyplot as plt
        import numpy as np

        # Create figure with larger size for better readability
        fig, ax = plt.subplots(1, 1, figsize=(16, 10))

        trade_numbers = journey_data['trade_numbers']
        max_up = journey_data['max_up_points']
        max_down = journey_data['max_down_points']
        exits = journey_data['exit_points']

        # Create x-axis positions
        x_pos = np.arange(len(trade_numbers))
        bar_width = 0.8

        # Plot bars for each trade showing the full range from max down to max up
        for i in range(len(trade_numbers)):
            # Determine color based on trade outcome
            if i in journey_data['winning_trades']:
                color = 'green'
                alpha = 0.7
            elif i in journey_data['losing_trades']:
                color = 'red'
                alpha = 0.7
            else:
                color = 'gray'
                alpha = 0.7

            # Draw vertical bar from max_down to max_up
            bottom = max_down[i]
            height = max_up[i] - max_down[i]

            ax.bar(x_pos[i], height, bottom=bottom, width=bar_width,
                  color=color, alpha=alpha, edgecolor='black', linewidth=0.5)

            # Mark the exit point with a horizontal line
            exit_color = 'darkgreen' if exits[i] > 0 else 'darkred' if exits[i] < 0 else 'black'
            ax.hlines(exits[i], x_pos[i] - bar_width/2, x_pos[i] + bar_width/2,
                     colors=exit_color, linewidth=3, alpha=0.9)

        # Add zero line
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=1)

        # Formatting
        ax.set_xlabel('Trade Number', fontsize=12)
        ax.set_ylabel('Points from Entry Price', fontsize=12)
        ax.set_title('Trade Journey Analysis - Maximum Price Movements & Exit Points',
                    fontsize=14, fontweight='bold')

        # Set x-axis ticks and labels
        ax.set_xticks(x_pos[::max(1, len(trade_numbers)//20)])  # Show every nth tick for readability
        ax.set_xticklabels([str(trade_numbers[i]) for i in range(0, len(trade_numbers), max(1, len(trade_numbers)//20))])

        # Increase y-axis tick density for better granularity
        import numpy as np
        y_min = min(min(max_down), min(exits)) if max_down and exits else 0
        y_max = max(max(max_up), max(exits)) if max_up and exits else 0

        # Create very high density y-axis ticks
        if y_max - y_min > 0:
            # Calculate appropriate tick interval based on range - much higher density
            y_range = y_max - y_min
            if y_range <= 10:
                tick_interval = 0.5  # Every 0.5 points for very small ranges
            elif y_range <= 20:
                tick_interval = 1  # Every 1 point for small ranges
            elif y_range <= 50:
                tick_interval = 2  # Every 2 points for medium ranges
            elif y_range <= 100:
                tick_interval = 5  # Every 5 points for larger ranges
            else:
                tick_interval = 10  # Every 10 points for very large ranges

            # Generate tick positions
            tick_start = int(np.floor(y_min / tick_interval)) * tick_interval
            tick_end = int(np.ceil(y_max / tick_interval)) * tick_interval
            y_ticks = np.arange(tick_start, tick_end + tick_interval, tick_interval)
            ax.set_yticks(y_ticks)

        ax.grid(True, alpha=0, axis='y')  # Transparent grid (change to 0.3 to make visible)

        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='green', alpha=0.7, label='Winning Trades'),
            Patch(facecolor='red', alpha=0.7, label='Losing Trades'),
            plt.Line2D([0], [0], color='darkgreen', linewidth=3, label='Exit Point (Win)'),
            plt.Line2D([0], [0], color='darkred', linewidth=3, label='Exit Point (Loss)')
        ]
        if journey_data['breakeven_trades']:
            legend_elements.append(Patch(facecolor='gray', alpha=0.7, label='Breakeven Trades'))

        ax.legend(handles=legend_elements, loc='upper right')

        # Add statistics text box
        stats_text = self._create_journey_stats_text(journey_data)
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

        # Save the chart
        plt.tight_layout()
        plt.savefig('backtest/stats/trade_journey.png', dpi=300, bbox_inches='tight')
        plt.close()

    def _create_journey_stats_text(self, journey_data: dict) -> str:
        """Create summary statistics text for trade journey chart."""
        import numpy as np

        max_up = journey_data['max_up_points']
        max_down = journey_data['max_down_points']
        exits = journey_data['exit_points']

        stats_lines = ["Trade Journey Summary"]
        stats_lines.append(f"Total Trades: {journey_data['total_trades']}")
        stats_lines.append("")

        # Maximum movement statistics (true max movements from entry)
        if max_up:
            avg_max_up = np.mean(max_up)
            max_max_up = np.max(max_up)
            stats_lines.append("Max Positive Movement:")
            stats_lines.append(f"  Average: {avg_max_up:.1f} pts")
            stats_lines.append(f"  Highest: {max_max_up:.1f} pts")
            stats_lines.append("")

        if max_down:
            avg_max_down = np.mean([abs(x) for x in max_down])
            max_max_down = np.max([abs(x) for x in max_down])
            stats_lines.append("Max Negative Movement:")
            stats_lines.append(f"  Average: {avg_max_down:.1f} pts")
            stats_lines.append(f"  Worst: {max_max_down:.1f} pts")
            stats_lines.append("")

        # Exit point statistics
        if exits:
            avg_exit = np.mean(exits)
            best_exit = np.max(exits)
            worst_exit = np.min(exits)
            stats_lines.append("Exit Points:")
            stats_lines.append(f"  Average: {avg_exit:.1f} pts")
            stats_lines.append(f"  Best: {best_exit:.1f} pts")
            stats_lines.append(f"  Worst: {worst_exit:.1f} pts")

        return "\n".join(stats_lines)

    def _cleanup_backtest_folders(self) -> None:
        """Clean up existing backtest folders before generating new charts.

        This ensures each backtest run starts with clean folders and prevents
        mixing results from different strategy runs.
        """
        import shutil

        folders_to_clean = [
            "backtest/trade_charts",
            "backtest/biggest_winners",
            "backtest/biggest_losers",
            "backtest/stats"
        ]

        for folder in folders_to_clean:
            if os.path.exists(folder):
                try:
                    shutil.rmtree(folder)
                    logger.info(f"Cleaned up existing folder: {folder}")
                except Exception as e:
                    logger.warning(f"Could not clean up folder {folder}: {e}")

    def _get_trade_number(self, trade) -> int:
        """Get the trade number for a given trade object."""
        completed_trades = self.get_completed_trades()
        for i, t in enumerate(completed_trades, 1):
            if (t.entry_time == trade.entry_time and
                t.exit_time == trade.exit_time and
                t.realized_pnl == trade.realized_pnl):
                return i
        return None

    def _calculate_drawdown_metrics(self, completed_trades: list) -> dict:
        """Calculate drawdown metrics from completed trades.

        Args:
            completed_trades: List of completed Trade objects

        Returns:
            dict: Dictionary with drawdown metrics or None if no trades
        """
        if not completed_trades:
            return None

        # Calculate running P&L
        running_pnl = 0
        peak_pnl = 0
        max_drawdown = 0
        drawdown_start = 0
        max_drawdown_duration = 0
        current_drawdown_duration = 0

        for i, trade in enumerate(completed_trades):
            running_pnl += trade.realized_pnl

            # Update peak
            if running_pnl > peak_pnl:
                peak_pnl = running_pnl
                current_drawdown_duration = 0
            else:
                current_drawdown_duration += 1

            # Calculate current drawdown
            current_drawdown = peak_pnl - running_pnl

            # Update maximum drawdown
            if current_drawdown > max_drawdown:
                max_drawdown = current_drawdown
                max_drawdown_duration = current_drawdown_duration

        return {
            'max_drawdown': max_drawdown,
            'drawdown_duration': max_drawdown_duration,
        }

    def _print_trade_distribution(self, completed_trades: list) -> None:
        """Print trade P&L distribution analysis.

        Args:
            completed_trades: List of completed Trade objects
        """
        if not completed_trades:
            return

        # Define P&L buckets
        pnl_values = [trade.realized_pnl for trade in completed_trades]

        # Count trades in different P&L ranges
        big_winners = sum(1 for pnl in pnl_values if pnl >= 50)
        small_winners = sum(1 for pnl in pnl_values if 0 < pnl < 50)
        break_even = sum(1 for pnl in pnl_values if pnl == 0)
        small_losers = sum(1 for pnl in pnl_values if -50 < pnl < 0)
        big_losers = sum(1 for pnl in pnl_values if pnl <= -50)

        total_trades = len(completed_trades)

        print(f"  Big Winners (≥$50): {big_winners} ({big_winners/total_trades*100:.1f}%)")
        print(f"  Small Winners ($0-$50): {small_winners} ({small_winners/total_trades*100:.1f}%)")
        if break_even > 0:
            print(f"  Break-even ($0): {break_even} ({break_even/total_trades*100:.1f}%)")
        print(f"  Small Losers ($0 to -$50): {small_losers} ({small_losers/total_trades*100:.1f}%)")
        print(f"  Big Losers (≤-$50): {big_losers} ({big_losers/total_trades*100:.1f}%)")

        # Calculate percentiles
        sorted_pnl = sorted(pnl_values)
        n = len(sorted_pnl)
        if n >= 4:
            p25 = sorted_pnl[int(n * 0.25)]
            p75 = sorted_pnl[int(n * 0.75)]
            print(f"  25th Percentile: ${p25:.2f}")
            print(f"  75th Percentile: ${p75:.2f}")

    def _print_mae_mfe_analysis(self, completed_trades: list) -> None:
        """Print Maximum Adverse Excursion and Maximum Favorable Excursion analysis.

        This analysis helps determine optimal stop-loss and take-profit levels.

        Args:
            completed_trades: List of completed Trade objects
        """
        if not completed_trades:
            return

        winning_trades = [t for t in completed_trades if t.realized_pnl > 0]
        losing_trades = [t for t in completed_trades if t.realized_pnl < 0]

        # Get point value for conversion
        point_value = self._contract_specifications.point_value if self._contract_specifications else 1.0

        # MAE Analysis for winning trades (key for stop-loss optimization)
        if winning_trades:
            winning_mae_values = [t.max_adverse_excursion for t in winning_trades]
            max_winning_mae = max(winning_mae_values)
            avg_winning_mae = sum(winning_mae_values) / len(winning_mae_values)

            # Calculate percentiles for winning trade MAE
            sorted_winning_mae = sorted(winning_mae_values)
            n = len(sorted_winning_mae)
            mae_90th = sorted_winning_mae[int(n * 0.9)] if n >= 10 else max_winning_mae
            mae_95th = sorted_winning_mae[int(n * 0.95)] if n >= 20 else max_winning_mae

            print(f"  Winning Trades MAE (Stop-Loss Analysis):")
            print(f"    Average MAE: ${avg_winning_mae:.2f} ({avg_winning_mae/point_value:.1f} pts)")
            print(f"    Maximum MAE: ${max_winning_mae:.2f} ({max_winning_mae/point_value:.1f} pts)")
            print(f"    90th Percentile MAE: ${mae_90th:.2f} ({mae_90th/point_value:.1f} pts)")
            print(f"    95th Percentile MAE: ${mae_95th:.2f} ({mae_95th/point_value:.1f} pts)")

            # Count how many winning trades would be stopped out at different levels (in points)
            stop_levels_points = [5, 10, 15, 20, 25, 30, 40, 50]
            stop_levels_dollars = [pts * point_value for pts in stop_levels_points]
            print(f"    Stop-Loss Impact Analysis:")
            for pts, dollars in zip(stop_levels_points, stop_levels_dollars):
                stopped_out = sum(1 for mae in winning_mae_values if mae > dollars)
                percentage = (stopped_out / len(winning_trades)) * 100
                print(f"      {pts} pts (${dollars:.0f}) stop: {stopped_out}/{len(winning_trades)} winners stopped ({percentage:.1f}%)")

        # MAE Analysis for losing trades
        if losing_trades:
            losing_mae_values = [t.max_adverse_excursion for t in losing_trades]
            max_losing_mae = max(losing_mae_values)
            avg_losing_mae = sum(losing_mae_values) / len(losing_mae_values)

            print(f"  Losing Trades MAE:")
            print(f"    Average MAE: ${avg_losing_mae:.2f} ({avg_losing_mae/point_value:.1f} pts)")
            print(f"    Maximum MAE: ${max_losing_mae:.2f} ({max_losing_mae/point_value:.1f} pts)")

        # MFE Analysis for losing trades (missed profit opportunities)
        if losing_trades:
            losing_mfe_values = [t.max_favorable_excursion for t in losing_trades]
            max_losing_mfe = max(losing_mfe_values)
            avg_losing_mfe = sum(losing_mfe_values) / len(losing_mfe_values)

            print(f"  Losing Trades MFE (Missed Opportunities):")
            print(f"    Average MFE: ${avg_losing_mfe:.2f} ({avg_losing_mfe/point_value:.1f} pts)")
            print(f"    Maximum MFE: ${max_losing_mfe:.2f} ({max_losing_mfe/point_value:.1f} pts)")

            # Count how many losing trades could have been profitable (in points)
            profit_levels_points = [5, 10, 15, 20, 25]
            profit_levels_dollars = [pts * point_value for pts in profit_levels_points]
            print(f"    Take-Profit Opportunity Analysis:")
            for pts, dollars in zip(profit_levels_points, profit_levels_dollars):
                could_profit = sum(1 for mfe in losing_mfe_values if mfe > dollars)
                percentage = (could_profit / len(losing_trades)) * 100
                print(f"      {pts} pts (${dollars:.0f}) target: {could_profit}/{len(losing_trades)} losers had profit ({percentage:.1f}%)")

    # =============================================================================
    # PUBLIC ORDER MANAGEMENT
    # =============================================================================

    def submit_order(self, order: OrderBase) -> None:
        """Submit an order for execution.

        Orders are queued and will be processed during the next bar.

        Args:
            order: The order to submit (MarketOrder, LimitOrder, or StopOrder)
        """
        # Route the order to the appropriate pending orders collection
        # Orders will be processed during the next bar's _process_pending_orders() call
        if isinstance(order, MarketOrder):
            self.pending_market_orders[order.order_id] = order
        elif isinstance(order, LimitOrder):
            self.pending_limit_orders[order.order_id] = order
        elif isinstance(order, StopOrder):
            self.pending_stop_orders[order.order_id] = order

    def cancel_order(self, order_id: uuid.UUID, reason: str = "Manual cancellation", current_time: pd.Timestamp = None) -> bool:
        """Cancel a pending order by its ID.

        Searches through all pending order collections and removes the order
        if found. This allows cancellation without knowing the order type.

        Args:
            order_id: Unique identifier of the order to cancel
            reason: Reason for cancellation (for tracking purposes)
            current_time: Current timestamp (auto-generated if None)

        Returns:
            bool: True if order was found and cancelled, False if not found
        """
        if current_time is None:
            current_time = pd.Timestamp.now()

        # Check market orders
        if order_id in self.pending_market_orders:
            cancelled_order = self.pending_market_orders.pop(order_id)
            self._record_cancellation(cancelled_order, OrderType.MARKET, reason, current_time)
            logger.debug(f"Cancelled market order: {cancelled_order}")
            return True

        # Check limit orders
        if order_id in self.pending_limit_orders:
            cancelled_order = self.pending_limit_orders.pop(order_id)
            self._record_cancellation(cancelled_order, OrderType.LIMIT, reason, current_time)
            logger.debug(f"Cancelled limit order: {cancelled_order}")
            return True

        # Check stop orders
        if order_id in self.pending_stop_orders:
            cancelled_order = self.pending_stop_orders.pop(order_id)
            self._record_cancellation(cancelled_order, OrderType.STOP, reason, current_time)
            logger.debug(f"Cancelled stop order: {cancelled_order}")
            return True

        # Order not found
        logger.warning(f"Order {order_id} not found for cancellation")
        return False

    def cancel_all_orders(self) -> int:
        """Cancel all pending orders of all types.

        This is useful for emergency exits or strategy resets.

        Returns:
            int: Total number of orders cancelled
        """
        total_cancelled = 0

        # Cancel all market orders
        market_count = len(self.pending_market_orders)
        self.pending_market_orders.clear()
        total_cancelled += market_count

        # Cancel all limit orders
        limit_count = len(self.pending_limit_orders)
        self.pending_limit_orders.clear()
        total_cancelled += limit_count

        # Cancel all stop orders
        stop_count = len(self.pending_stop_orders)
        self.pending_stop_orders.clear()
        total_cancelled += stop_count

        if total_cancelled > 0:
            logger.info(f"Cancelled all orders: {market_count} market, {limit_count} limit, {stop_count} stop")

        return total_cancelled

    def cancel_orders_by_type(self, order_type: OrderType) -> int:
        """Cancel all pending orders of a specific type.

        Args:
            order_type: Type of orders to cancel (MARKET, LIMIT, or STOP)

        Returns:
            int: Number of orders cancelled

        Raises:
            ValueError: If order_type is not recognized
        """
        if order_type == OrderType.MARKET:
            count = len(self.pending_market_orders)
            self.pending_market_orders.clear()
            logger.info(f"Cancelled {count} market orders")
            return count

        elif order_type == OrderType.LIMIT:
            count = len(self.pending_limit_orders)
            self.pending_limit_orders.clear()
            logger.info(f"Cancelled {count} limit orders")
            return count

        elif order_type == OrderType.STOP:
            count = len(self.pending_stop_orders)
            self.pending_stop_orders.clear()
            logger.info(f"Cancelled {count} stop orders")
            return count

        else:
            raise ValueError(f"Unknown order type: {order_type}")

    def get_pending_order_count(self) -> dict[OrderType, int]:
        """Get count of pending orders by type.

        Returns:
            dict: Dictionary mapping order types to their counts
        """
        return {
            OrderType.MARKET: len(self.pending_market_orders),
            OrderType.LIMIT: len(self.pending_limit_orders),
            OrderType.STOP: len(self.pending_stop_orders),
        }

    def get_pending_orders(self) -> dict[OrderType, dict[uuid.UUID, OrderBase]]:
        """Get all pending orders organized by type.

        Returns:
            dict: Dictionary mapping order types to their pending orders
        """
        return {
            OrderType.MARKET: self.pending_market_orders.copy(),
            OrderType.LIMIT: self.pending_limit_orders.copy(),
            OrderType.STOP: self.pending_stop_orders.copy(),
        }

    def _record_cancellation(self, order: OrderBase, order_type: OrderType, reason: str, current_time: pd.Timestamp):
        """Record an order cancellation for tracking and analysis.

        Args:
            order: The cancelled order
            order_type: Type of the cancelled order
            reason: Reason for cancellation
            current_time: When the cancellation occurred
        """
        cancellation = OrderCancellation(
            cancellation_id=uuid.uuid4(),
            ts_event=current_time,
            cancelled_order_id=order.order_id,
            order_type=order_type,
            cancellation_reason=reason,
            original_order=order,
        )

        # Add to buffer for batch processing
        self._cancellations_buffer.append(cancellation.__dict__)

        # Flush buffer if it gets large
        if len(self._cancellations_buffer) >= 1000:
            self._flush_cancellations_buffer()

    def _flush_cancellations_buffer(self):
        """Flush the cancellations buffer to the main cancellations DataFrame.

        This method converts the buffered cancellation records to a DataFrame and appends
        them to the main cancellations DataFrame. The buffer is cleared after flushing.
        """
        if self._cancellations_buffer:
            # Convert buffered cancellations to DataFrame
            buffer_df = pd.DataFrame(self._cancellations_buffer)

            # Append to main cancellations DataFrame
            if self._cancellations_df.empty:
                self._cancellations_df = buffer_df
            else:
                # Use concat for better performance than repeated appends
                self._cancellations_df = pd.concat(
                    [self._cancellations_df, buffer_df], ignore_index=True
                )

            # Clear the buffer after flushing
            self._cancellations_buffer = []

    def _update_trade_tracking(self, fill: OrderFill, current_price: float = None):
        """Update trade tracking based on order execution.

        This method handles the complete trade lifecycle from flat to flat,
        including adds and reductions to positions.

        Args:
            fill: OrderFill object containing execution details
            current_price: Current market price for unrealized P&L calculation
        """
        current_position = self.get_current_position()

        # Determine if this fill opens a new trade, adds to existing, or closes
        if self._current_trade is None and current_position != 0:
            # Opening a new trade (was flat, now have position)
            self._open_new_trade(fill)

        elif self._current_trade is not None and current_position == 0:
            # Closing the current trade (had position, now flat)
            self._close_current_trade(fill)

        elif self._current_trade is not None and current_position != 0:
            # Adding to or reducing existing trade
            self._update_existing_trade(fill)

        # Update unrealized P&L for open trade
        if self._current_trade and current_price:
            self._update_unrealized_pnl(current_price)

    def _open_new_trade(self, fill: OrderFill):
        """Open a new trade with the given fill.

        Args:
            fill: OrderFill that opens the new trade
        """
        self._current_trade = Trade(
            trade_id=uuid.uuid4(),
            entry_time=fill.ts_event,
            direction=fill.trade_direction,
            max_quantity=abs(fill.quantity),
            entry_fills=[fill],
            exit_fills=[],
            total_commission=fill.commission_and_fees,
            weighted_avg_entry_price=fill.fill_at,
        )

        logger.debug(f"Opened new trade: {self._current_trade.trade_id}")

    def _close_current_trade(self, fill: OrderFill):
        """Close the current trade with the given fill.

        Args:
            fill: OrderFill that closes the trade
        """
        if not self._current_trade:
            logger.warning("Attempting to close trade but no current trade exists")
            return

        # Add the closing fill
        self._current_trade.exit_fills.append(fill)
        self._current_trade.total_commission += fill.commission_and_fees
        self._current_trade.exit_time = fill.ts_event
        self._current_trade.duration = fill.ts_event - self._current_trade.entry_time
        self._current_trade.is_open = False

        # Calculate weighted average exit price
        total_exit_quantity = sum(f.quantity for f in self._current_trade.exit_fills)
        total_exit_value = sum(f.fill_at * f.quantity for f in self._current_trade.exit_fills)
        self._current_trade.weighted_avg_exit_price = total_exit_value / total_exit_quantity

        # Calculate realized P&L
        self._calculate_realized_pnl()

        # Update trade statistics
        self._trade_stats.total_trades += 1
        if self._current_trade.realized_pnl > 0:
            self._trade_stats.winning_trades += 1
        elif self._current_trade.realized_pnl < 0:
            self._trade_stats.losing_trades += 1

        # Move to completed trades
        self._completed_trades.append(self._current_trade)
        logger.debug(f"Closed trade: {self._current_trade.trade_id}, P&L: {self._current_trade.realized_pnl:.2f}")

        # Clear current trade
        self._current_trade = None

    def _update_existing_trade(self, fill: OrderFill):
        """Update existing trade with add or reduction.

        Args:
            fill: OrderFill that modifies the existing trade
        """
        if not self._current_trade:
            logger.warning("Attempting to update trade but no current trade exists")
            return

        current_position = abs(self.get_current_position())

        # Determine if this is an add or reduction
        if fill.trade_direction == self._current_trade.direction:
            # Adding to position
            self._current_trade.entry_fills.append(fill)

            # Recalculate weighted average entry price
            total_entry_quantity = sum(f.quantity for f in self._current_trade.entry_fills)
            total_entry_value = sum(f.fill_at * f.quantity for f in self._current_trade.entry_fills)
            self._current_trade.weighted_avg_entry_price = total_entry_value / total_entry_quantity

            logger.debug(f"Added to trade: {self._current_trade.trade_id}")

        else:
            # Reducing position (partial exit)
            self._current_trade.exit_fills.append(fill)
            logger.debug(f"Reduced trade: {self._current_trade.trade_id}")

        # Update max quantity and commission
        self._current_trade.max_quantity = max(self._current_trade.max_quantity, current_position)
        self._current_trade.total_commission += fill.commission_and_fees

    def _calculate_realized_pnl(self):
        """Calculate realized P&L for the current trade."""
        if not self._current_trade:
            return

        # Calculate total entry and exit values
        total_entry_quantity = sum(f.quantity for f in self._current_trade.entry_fills)
        total_entry_value = sum(f.fill_at * f.quantity for f in self._current_trade.entry_fills)

        total_exit_quantity = sum(f.quantity for f in self._current_trade.exit_fills)
        total_exit_value = sum(f.fill_at * f.quantity for f in self._current_trade.exit_fills)

        # Calculate P&L based on direction
        if self._current_trade.direction == Side.BUY:
            # Long trade: profit when exit price > entry price
            gross_pnl = total_exit_value - total_entry_value
        else:
            # Short trade: profit when entry price > exit price
            gross_pnl = total_entry_value - total_exit_value

        # Apply point value to convert to currency
        if self._contract_specifications:
            gross_pnl *= self._contract_specifications.point_value

        # Subtract total commissions
        self._current_trade.realized_pnl = gross_pnl - self._current_trade.total_commission

    def _update_unrealized_pnl(self, current_price: float):
        """Update unrealized P&L and MAE/MFE for the current open trade.

        Args:
            current_price: Current market price
        """
        if not self._current_trade or not self._contract_specifications:
            return

        current_position = self.get_current_position()
        if current_position == 0:
            self._current_trade.unrealized_pnl = 0.0
            return

        # Calculate unrealized P&L
        entry_price = self._current_trade.weighted_avg_entry_price

        if self._current_trade.direction == Side.BUY:
            # Long position: profit when current price > entry price
            price_diff = current_price - entry_price
        else:
            # Short position: profit when entry price > current price
            price_diff = entry_price - current_price

        # Convert to currency and account for position size
        gross_unrealized = price_diff * abs(current_position) * self._contract_specifications.point_value

        # Note: We don't subtract commissions from unrealized P&L as they're already paid
        self._current_trade.unrealized_pnl = gross_unrealized

        # Update Maximum Adverse Excursion (MAE) - worst unrealized loss
        if gross_unrealized < 0:
            # Trade is currently losing
            adverse_excursion = abs(gross_unrealized)
            self._current_trade.max_adverse_excursion = max(
                self._current_trade.max_adverse_excursion, adverse_excursion
            )

        # Update Maximum Favorable Excursion (MFE) - best unrealized profit
        if gross_unrealized > 0:
            # Trade is currently winning
            self._current_trade.max_favorable_excursion = max(
                self._current_trade.max_favorable_excursion, gross_unrealized
            )

    def _close_open_trade_at_end(self):
        """Close any open trade at the end of backtest for analysis.

        This creates a synthetic exit fill at the last market price to properly
        close the trade for P&L calculation and analysis purposes.
        """
        if not self._current_trade or self.get_current_position() == 0:
            return

        # Get the last market price from the data
        if self._market_data_df.empty:
            logger.warning("No market data available to close open trade")
            return

        last_bar = self._market_data_df.iloc[-1]
        last_price = last_bar['close']
        last_time = last_bar['ts_event']

        # Create synthetic exit fill to close the position
        current_position = self.get_current_position()
        exit_direction = Side.SELL if current_position > 0 else Side.BUY

        synthetic_fill = OrderFill(
            fill_id=uuid.uuid4(),
            ts_event=last_time,
            associated_order_id=uuid.uuid4(),  # Synthetic order ID
            trade_direction=exit_direction,
            quantity=abs(current_position),
            fill_at=last_price,
            commission_and_fees=0.0,  # No commission for synthetic close
            fill_point_value_adjusted_for_commission_and_fees=last_price,
        )

        # Close the trade with synthetic fill
        self._close_current_trade(synthetic_fill)

        logger.info(f"Closed open trade at end of backtest at price {last_price:.2f}")

    def _create_individual_trade_chart(
        self, trade: Trade, trade_num: int, lookback_bars: int, lookforward_bars: int
    ) -> None:
        """Create a detailed chart for an individual trade.

        Args:
            trade: Trade object to chart
            trade_num: Trade number for filename
            lookback_bars: Bars to show before entry
            lookforward_bars: Bars to show after exit
        """
        # Find the data range for this trade
        trade_start_time = trade.entry_time
        trade_end_time = trade.exit_time

        # Find indices in market data
        start_mask = self._market_data_df['ts_event'] >= trade_start_time
        end_mask = self._market_data_df['ts_event'] <= trade_end_time

        if not start_mask.any() or not end_mask.any():
            logger.warning(f"Cannot find trade data for trade {trade_num}")
            return

        trade_start_idx = self._market_data_df[start_mask].index[0]
        trade_end_idx = self._market_data_df[end_mask].index[-1]

        # Convert pandas indices to positions in the DataFrame
        trade_start_pos = self._market_data_df.index.get_loc(trade_start_idx)
        trade_end_pos = self._market_data_df.index.get_loc(trade_end_idx)

        # Calculate chart data range with lookback/lookforward
        chart_start_pos = max(0, trade_start_pos - lookback_bars)
        chart_end_pos = min(len(self._market_data_df) - 1, trade_end_pos + lookforward_bars)

        # Extract chart data
        chart_data = self._market_data_df.iloc[chart_start_pos:chart_end_pos + 1].copy()

        if chart_data.empty:
            logger.warning(f"No chart data available for trade {trade_num}")
            return

        # Get fills for this trade
        trade_fills = trade.entry_fills + trade.exit_fills

        # Create the chart
        self._plot_trade_chart(chart_data, trade, trade_fills, trade_num,
                              trade_start_pos - chart_start_pos,
                              trade_end_pos - chart_start_pos)

    def _plot_trade_chart(
        self, chart_data: pd.DataFrame, trade: Trade, trade_fills: list,
        trade_num: int, highlight_start: int, highlight_end: int
    ) -> None:
        """Plot the actual trade chart with all visual elements.

        Args:
            chart_data: Market data for the chart period
            trade: Trade object with details
            trade_fills: List of OrderFill objects for this trade
            trade_num: Trade number for title and filename
            highlight_start: Index where trade period starts in chart_data
            highlight_end: Index where trade period ends in chart_data
        """
        # Identify indicators by their prefix
        main_indicators = [col for col in chart_data.columns if col.startswith('I00_')]

        # Group subplot indicators by their number
        subplot_indicators = {}
        for col in chart_data.columns:
            if (col.startswith('I') and len(col) > 3 and
                col[1:3].isdigit() and col[0:3] not in ['I00', 'I99']):
                subplot_num = int(col[1:3])
                if subplot_num not in subplot_indicators:
                    subplot_indicators[subplot_num] = []
                subplot_indicators[subplot_num].append(col)

        # Calculate number of subplots needed (P&L + main + indicators)
        num_subplots = 2 + len(subplot_indicators)  # P&L + Main chart + indicator subplots

        # Create figure with appropriate height ratios (P&L first, then main, then indicators)
        height_ratios = [1, 4] + [1] * len(subplot_indicators)  # P&L small, Main larger, indicators small
        fig, axes = plt.subplots(
            num_subplots, 1, figsize=(16, 12), sharex=True,
            gridspec_kw={'height_ratios': height_ratios}
        )

        if num_subplots == 1:
            axes = [axes]

        # Plot P&L tracking chart (now first/top)
        ax_pnl = axes[0]
        self._plot_pnl_tracking(ax_pnl, chart_data, trade, highlight_start, highlight_end)

        # Plot main price chart (now second)
        ax_main = axes[1]
        self._plot_price_data(ax_main, chart_data, highlight_start, highlight_end)
        self._plot_main_indicators(ax_main, chart_data, main_indicators)
        self._plot_trade_markers_and_lines(ax_main, chart_data, trade, trade_fills)
        self._plot_break_even_lines(ax_main, chart_data)

        # Plot indicator subplots (now starting from axes[2])
        for i, (subplot_num, indicators) in enumerate(sorted(subplot_indicators.items())):
            ax = axes[i + 2]
            self._plot_subplot_indicators(ax, chart_data, indicators, subplot_num)

        # Format and save chart (ax_main is now axes[1])
        self._format_and_save_chart(fig, axes, trade, trade_num, chart_data)

    def _plot_price_data(self, ax, chart_data: pd.DataFrame, highlight_start: int, highlight_end: int):
        """Plot OHLC price data as high-low bars."""
        # Plot high-low bars
        for i in range(len(chart_data)):
            date = chart_data['ts_event'].iloc[i]
            high = chart_data['high'].iloc[i]
            low = chart_data['low'].iloc[i]
            close = chart_data['close'].iloc[i]

            # Plot high-low range as thin vertical line
            ax.plot([date, date], [low, high], color='black', linewidth=0.8, alpha=0.7)

            # Plot close price as small horizontal tick
            ax.plot([date], [close], marker='_', color='blue', markersize=3)

        # Highlight trade period with background color
        if 0 <= highlight_start < len(chart_data) and 0 <= highlight_end < len(chart_data):
            start_time = mdates.date2num(chart_data['ts_event'].iloc[highlight_start])
            end_time = mdates.date2num(chart_data['ts_event'].iloc[highlight_end])
            y_min, y_max = ax.get_ylim()
            rect = Rectangle(
                (start_time, y_min), end_time - start_time, y_max - y_min,
                facecolor='lightblue', alpha=0.2, label='Trade Period'
            )
            ax.add_patch(rect)

    def _plot_main_indicators(self, ax, chart_data: pd.DataFrame, main_indicators: list):
        """Plot main indicators on the price chart."""
        colors = ['orange', 'purple', 'brown', 'pink', 'gray']

        # Create better labels for common indicators
        label_map = {
            'I00_fast_ma': '20 MA',
            'I00_slow_ma': '50 MA',
            'I00_trend_ma': '100 MA'
        }

        for i, indicator in enumerate(main_indicators):
            color = colors[i % len(colors)]
            # Use mapped label if available, otherwise format the indicator name
            if indicator in label_map:
                label = label_map[indicator]
            else:
                label = self._format_indicator_name(indicator[4:])  # Remove I00_ prefix and format
            ax.plot(
                chart_data['ts_event'], chart_data[indicator],
                label=label, linewidth=1.5, alpha=0.8, color=color
            )

    def _plot_trade_markers_and_lines(self, ax, chart_data: pd.DataFrame, trade: Trade, trade_fills: list):
        """Plot trade entry/exit markers and connecting lines with P&L color coding."""
        entry_times = []
        entry_prices = []
        exit_times = []
        exit_prices = []

        # Plot individual fills as markers with size representing quantity
        for fill in trade_fills:
            if fill in trade.entry_fills:
                marker = '^' if fill.trade_direction == Side.BUY else 'v'
                color = 'green'
                entry_times.append(fill.ts_event)
                entry_prices.append(fill.fill_at)
                label_prefix = "Entry"
            else:  # exit fill
                marker = 'v' if fill.trade_direction == Side.SELL else '^'
                color = 'red'
                exit_times.append(fill.ts_event)
                exit_prices.append(fill.fill_at)
                label_prefix = "Exit"

            # Scale marker size based on quantity (min 80, max 300)
            base_size = 120
            quantity_multiplier = min(3.0, max(0.5, fill.quantity))
            size = base_size * quantity_multiplier

            ax.scatter(fill.ts_event, fill.fill_at, marker=marker, color=color,
                      s=size, edgecolors='black', linewidth=1, zorder=5,
                      alpha=0.8)

            # Add quantity label next to marker
            offset_y = (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.02
            ax.annotate(f'{fill.quantity}',
                       (fill.ts_event, fill.fill_at + offset_y),
                       ha='center', va='bottom', fontsize=8, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))

        # Trade line connecting entry to exit removed for cleaner charts
        # (Previous code drew a line from weighted avg entry to exit price)

    def _plot_break_even_lines(self, ax, chart_data: pd.DataFrame):
        """Plot break-even lines when in position."""
        if 'break_even' not in chart_data.columns:
            return

        for i in range(len(chart_data) - 1):
            if (pd.notna(chart_data['break_even'].iloc[i]) and
                chart_data['position'].iloc[i] != 0):
                ax.hlines(
                    y=chart_data['break_even'].iloc[i],
                    xmin=chart_data['ts_event'].iloc[i],
                    xmax=chart_data['ts_event'].iloc[i + 1],
                    colors='purple', linestyles=':', alpha=0.7, linewidth=1
                )

    def _plot_pnl_tracking(self, ax, chart_data: pd.DataFrame, trade: Trade,
                          highlight_start: int, highlight_end: int):
        """Plot P&L tracking with unrealized P&L and drawdown."""
        if 'position' not in chart_data.columns:
            return

        # Calculate running P&L for the trade period
        pnl_series = []
        max_pnl = 0
        drawdown_series = []

        for i, row in chart_data.iterrows():
            if row['position'] == 0:
                # Flat position
                pnl = 0
                drawdown = 0
            else:
                # Calculate unrealized P&L from weighted average entry price
                if trade.weighted_avg_entry_price and self._contract_specifications:
                    price_diff = (row['close'] - trade.weighted_avg_entry_price
                                 if trade.direction == Side.BUY
                                 else trade.weighted_avg_entry_price - row['close'])
                    pnl = (price_diff * abs(row['position']) *
                          self._contract_specifications.point_value)
                else:
                    pnl = 0

                # Track maximum P&L and calculate drawdown
                max_pnl = max(max_pnl, pnl)
                drawdown = pnl - max_pnl

            pnl_series.append(pnl)
            drawdown_series.append(drawdown)

        # Plot P&L line
        ax.plot(chart_data['ts_event'], pnl_series, color='blue', linewidth=2,
               label='Unrealized P&L', alpha=0.8)

        # Plot drawdown as filled area
        ax.fill_between(chart_data['ts_event'], drawdown_series, 0,
                       color='red', alpha=0.3, label='Drawdown')

        # Add horizontal line at zero
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=0.8)

        # Highlight trade period
        if 0 <= highlight_start < len(chart_data) and 0 <= highlight_end < len(chart_data):
            start_time = mdates.date2num(chart_data['ts_event'].iloc[highlight_start])
            end_time = mdates.date2num(chart_data['ts_event'].iloc[highlight_end])
            y_min, y_max = ax.get_ylim()
            rect = Rectangle(
                (start_time, y_min), end_time - start_time, y_max - y_min,
                facecolor='lightblue', alpha=0.2
            )
            ax.add_patch(rect)

        ax.legend(loc='upper left')
        ax.grid(True, alpha=0)  # Transparent grid (change to 0.3 to make visible)

    def _plot_subplot_indicators(self, ax, chart_data: pd.DataFrame, indicators: list, subplot_num: int):
        """Plot indicators in their own subplot."""
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
        for i, indicator in enumerate(indicators):
            color = colors[i % len(colors)]
            # Format the indicator name for display
            formatted_name = self._format_indicator_name(indicator[4:])  # Remove I##_ prefix
            ax.plot(chart_data['ts_event'], chart_data[indicator],
                   label=formatted_name, linewidth=1, color=color)

        ax.legend(loc='upper left', fontsize=8)
        ax.grid(True, alpha=0)  # Transparent grid (change to 0.3 to make visible)

    def _format_indicator_name(self, raw_name: str) -> str:
        """Format indicator name for display in legend.

        Converts 'detrend_oscillator' to 'Detrend Oscillator'
        - Replaces underscores with spaces
        - Capitalizes first letter of each word
        - Preserves existing capitalization (for acronyms like ATR, RSI, etc.)

        Args:
            raw_name: Raw indicator name (e.g., 'detrend_oscillator', 'atr', 'rsi_ma')

        Returns:
            str: Formatted name (e.g., 'Detrend Oscillator', 'ATR', 'RSI MA')
        """
        # Replace underscores with spaces
        name_with_spaces = raw_name.replace('_', ' ')

        # Split into words
        words = name_with_spaces.split()

        # Capitalize each word, but preserve existing capitalization
        formatted_words = []
        for word in words:
            if word.isupper():
                # Keep acronyms as they are (e.g., ATR, RSI, MACD)
                formatted_words.append(word)
            elif word.islower():
                # Capitalize first letter of lowercase words
                formatted_words.append(word.capitalize())
            else:
                # Mixed case - keep as is (handles cases like 'MacD' if someone uses that)
                formatted_words.append(word)

        return ' '.join(formatted_words)

    def _format_and_save_chart(self, fig, axes, trade: Trade, trade_num: int, chart_data: pd.DataFrame):
        """Format the chart and save to file."""
        ax_pnl = axes[0]   # P&L chart is now at index 0 (top)
        ax_main = axes[1]  # Main chart is now at index 1 (middle)

        # Calculate trade statistics for title
        duration_minutes = trade.duration.total_seconds() / 60 if trade.duration else 0
        win_loss = "WIN" if trade.realized_pnl > 0 else "LOSS" if trade.realized_pnl < 0 else "BREAK-EVEN"

        # Create comprehensive title
        title = (f'Trade #{trade_num} - {win_loss} - '
                f'{trade.direction.value} - P&L: ${trade.realized_pnl:.2f} - '
                f'Duration: {duration_minutes:.0f}min')

        # Put title on the top chart (P&L chart)
        ax_pnl.set_title(title, fontsize=14, fontweight='bold')
        ax_main.grid(True, alpha=0)  # Transparent grid (change to 0.3 to make visible)

        # Create custom legend for trade markers
        custom_lines = [
            Line2D([0], [0], marker='^', color='w', markerfacecolor='green',
                  markersize=10, label='Entry (Buy)'),
            Line2D([0], [0], marker='v', color='w', markerfacecolor='green',
                  markersize=10, label='Entry (Sell)'),
            Line2D([0], [0], marker='v', color='w', markerfacecolor='red',
                  markersize=10, label='Exit (Sell)'),
            Line2D([0], [0], marker='^', color='w', markerfacecolor='red',
                  markersize=10, label='Exit (Buy)'),
            Line2D([0], [0], color='purple', linestyle=':', label='Break-even'),
            Line2D([0], [0], color='lightblue', marker='s', alpha=0.3,
                  markersize=10, label='Trade Period'),
        ]

        # Add trade statistics to legend
        stats_text = (f'Max Qty: {trade.max_quantity}\n'
                     f'Avg Entry: ${trade.weighted_avg_entry_price:.2f}\n'
                     f'Avg Exit: ${trade.weighted_avg_exit_price:.2f}\n'
                     f'Commission: ${trade.total_commission:.2f}\n'
                     f'Entry Fills: {len(trade.entry_fills)}\n'
                     f'Exit Fills: {len(trade.exit_fills)}')

        # Position legend and stats
        ax_main.legend(handles=custom_lines, loc='upper left', fontsize=9)
        ax_main.text(0.02, 0.02, stats_text, transform=ax_main.transAxes,
                    fontsize=9, verticalalignment='bottom',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        # Format x-axis with dates
        for ax in axes:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))

            # Set dense x-axis labels based on chart duration
            chart_duration_hours = (chart_data['ts_event'].iloc[-1] - chart_data['ts_event'].iloc[0]).total_seconds() / 3600

            if chart_duration_hours <= 2:
                # For short charts (<=2 hours): every 5 minutes
                ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
                ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=1))
            elif chart_duration_hours <= 8:
                # For medium charts (2-8 hours): every 15 minutes
                ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=15))
                ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=5))
            elif chart_duration_hours <= 24:
                # For day charts (8-24 hours): every hour
                ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=15))
            else:
                # For longer charts (>24 hours): every 4 hours
                ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
                ax.xaxis.set_minor_locator(mdates.HourLocator(interval=1))

        plt.xticks(rotation=90)
        plt.tight_layout()

        # Save with high DPI
        filename = f'backtest/trade_charts/trade_{trade_num:03d}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close(fig)

    def _cancel_expired_orders(self, current_time: pd.Timestamp):
        """Cancel orders that have passed their expiration time.

        Args:
            current_time: Current timestamp to check against expiration times
        """
        expired_orders = []

        # Check market orders for expiration
        for order_id, order in list(self.pending_market_orders.items()):
            if order.expiration_time is not None and current_time >= order.expiration_time:
                expired_orders.append((order_id, order, OrderType.MARKET))

        # Check limit orders for expiration
        for order_id, order in list(self.pending_limit_orders.items()):
            if order.expiration_time is not None and current_time >= order.expiration_time:
                expired_orders.append((order_id, order, OrderType.LIMIT))

        # Check stop orders for expiration
        for order_id, order in list(self.pending_stop_orders.items()):
            if order.expiration_time is not None and current_time >= order.expiration_time:
                expired_orders.append((order_id, order, OrderType.STOP))

        # Cancel all expired orders
        for order_id, order, order_type in expired_orders:
            if order_type == OrderType.MARKET:
                del self.pending_market_orders[order_id]
            elif order_type == OrderType.LIMIT:
                del self.pending_limit_orders[order_id]
            elif order_type == OrderType.STOP:
                del self.pending_stop_orders[order_id]

            # Record the cancellation
            self._record_cancellation(order, order_type, "Expired", current_time)
            logger.debug(f"Cancelled expired {order_type.value.lower()} order: {order_id}")

    # =============================================================================
    # PRIVATE IMPLEMENTATION METHODS
    # =============================================================================

    def _process_pending_orders(self, row):
        """Process all pending orders for the current bar.

        This method checks all pending orders (market, limit, and stop) and executes
        those that meet their execution criteria based on the current bar's OHLC data.
        Market orders are executed immediately at the open price. Limit and stop orders
        are executed if the bar's high/low prices trigger them.

        Also handles order expiration by cancelling orders that have passed their
        expiration time.

        Args:
            row: Current market data bar containing ts_event, open, high, low, close
        """
        # First, check for and cancel any expired orders
        self._cancel_expired_orders(row.ts_event)
        # Process market orders - these execute immediately at the open price
        for order_id, order in list(self.pending_market_orders.items()):
            fill = OrderFill(
                fill_id=uuid.uuid4(),
                ts_event=row.ts_event,
                associated_order_id=order.order_id,
                trade_direction=order.order_direction,
                quantity=order.quantity,
                fill_at=row.open,  # Market orders fill at open price
                commission_and_fees=(
                    self._contract_specifications.total_fees_per_contract_in_instrument_currency
                    * order.quantity
                ),
                # Calculate break-even price including commissions
                # For buys: add commission cost to entry price
                # For sells: subtract commission cost from entry price
                fill_point_value_adjusted_for_commission_and_fees=(
                    row.open
                    + self._contract_specifications.total_fees_per_contract_in_points
                    if order.order_direction == Side.BUY
                    else row.open
                    - self._contract_specifications.total_fees_per_contract_in_points
                ),
            )
            self._register_order_execution(fill)
            logger.debug(f"Executed market order: {fill}")
            del self.pending_market_orders[order_id]  # Remove from pending

        # Process limit orders - these execute only if price reaches the limit
        for order_id, order in list(self.pending_limit_orders.items()):
            # Check if limit order should be triggered based on bar's high/low
            # Buy limit: triggers when price drops to or below limit price
            # Sell limit: triggers when price rises to or above limit price
            if (order.order_direction == Side.BUY and row.low <= order.limit_price) or (
                order.order_direction == Side.SELL and row.high >= order.limit_price
            ):
                # Determine actual fill price (best case scenario for the trader)
                if order.order_direction == Side.BUY:
                    # Buy limit: fill at the better of limit price or open price
                    actual_fill_price = min(order.limit_price, row.open)
                else:
                    # Sell limit: fill at the better of limit price or open price
                    actual_fill_price = max(order.limit_price, row.open)

                fill = OrderFill(
                    fill_id=uuid.uuid4(),
                    ts_event=row.ts_event,
                    associated_order_id=order.order_id,
                    trade_direction=order.order_direction,
                    quantity=order.quantity,
                    fill_at=actual_fill_price,
                    commission_and_fees=(
                        self._contract_specifications.total_fees_per_contract_in_instrument_currency
                        * order.quantity
                    ),
                    fill_point_value_adjusted_for_commission_and_fees=(
                        actual_fill_price
                        + self._contract_specifications.total_fees_per_contract_in_points
                        if order.order_direction == Side.BUY
                        else actual_fill_price
                        - self._contract_specifications.total_fees_per_contract_in_points
                    ),
                )
                self._register_order_execution(fill)
                logger.debug(f"Executed limit order: {fill}")
                del self.pending_limit_orders[order_id]

        # Process stop orders - these become market orders when stop price is hit
        for order_id, order in list(self.pending_stop_orders.items()):
            # Check if stop order should be triggered based on bar's high/low
            # Buy stop: triggers when price rises to or above stop price (breakout)
            # Sell stop: triggers when price falls to or below stop price (stop loss)
            if (order.order_direction == Side.BUY and row.high >= order.stop_price) or (
                order.order_direction == Side.SELL and row.low <= order.stop_price
            ):
                # Determine actual fill price (worst case scenario - slippage)
                if order.order_direction == Side.BUY:
                    # Buy stop: fill at the worse of stop price or open price
                    actual_fill_price = max(order.stop_price, row.open)
                else:
                    # Sell stop: fill at the worse of stop price or open price
                    actual_fill_price = min(order.stop_price, row.open)

                fill = OrderFill(
                    fill_id=uuid.uuid4(),
                    ts_event=row.ts_event,
                    associated_order_id=order.order_id,
                    trade_direction=order.order_direction,
                    quantity=order.quantity,
                    fill_at=actual_fill_price,
                    commission_and_fees=(
                        self._contract_specifications.total_fees_per_contract_in_instrument_currency
                        * order.quantity
                    ),
                    fill_point_value_adjusted_for_commission_and_fees=(
                        actual_fill_price
                        + self._contract_specifications.total_fees_per_contract_in_points
                        if order.order_direction == Side.BUY
                        else actual_fill_price
                        - self._contract_specifications.total_fees_per_contract_in_points
                    ),
                )
                self._register_order_execution(fill)
                logger.debug(f"Executed stop order: {fill}")
                del self.pending_stop_orders[order_id]

    def _register_order_execution(self, fill: OrderFill):
        """Register an order execution and update internal state.

        This method records the order fill in the fills buffer, updates position
        tracking, trade tracking, and flushes buffers when they reach capacity.

        Args:
            fill: OrderFill object containing execution details
        """
        # Add fill to buffer for batch processing (performance optimization)
        self._fills_buffer.append(fill.__dict__)

        # Update position tracking with this fill
        self._update_positions(fill)

        # Update trade tracking with this fill
        # Use the fill price as current price for unrealized P&L calculation
        self._update_trade_tracking(fill, fill.fill_at)

        # Flush buffer to DataFrame when it gets large (batch processing for performance)
        if len(self._fills_buffer) >= 1000:
            self._flush_fills_buffer()

    def _update_positions(self, fill: OrderFill):
        """Update position tracking based on order execution.

        This method implements FIFO (First In, First Out) position management.
        When a fill occurs, it first attempts to close existing opposite positions
        before opening new positions in the fill direction. This ensures accurate
        position tracking and P&L calculations.

        Args:
            fill: OrderFill object containing execution details including direction,
                 quantity, price, and commission-adjusted price
        """
        remaining_quantity = fill.quantity

        if fill.trade_direction == Side.BUY:
            # BUY FILL: First close any existing short positions using FIFO
            # This implements First-In-First-Out position accounting
            while (
                remaining_quantity > 0
                and self._positions
                and self._positions[0].direction == Side.SELL
            ):
                position = self._positions[0]  # Always work with oldest position first

                # Determine how much of this short position to close
                quantity_to_close = min(position.quantity, remaining_quantity)
                remaining_quantity -= quantity_to_close

                # Update or remove the position based on how much we're closing
                if quantity_to_close < position.quantity:
                    # Partial close: reduce the position size
                    position.quantity -= quantity_to_close
                else:
                    # Complete close: remove the entire position
                    self._positions.popleft()

            # If we still have remaining quantity after closing shorts, open new long position
            if remaining_quantity > 0:
                self._positions.append(
                    Position(
                        entry_time=fill.ts_event,
                        direction=Side.BUY,
                        quantity=remaining_quantity,
                        entry_price=fill.fill_at,
                        adjusted_entry_price=fill.fill_point_value_adjusted_for_commission_and_fees,
                    )
                )
        else:  # SELL FILL
            # SELL FILL: First close any existing long positions using FIFO
            # This implements First-In-First-Out position accounting
            while (
                remaining_quantity > 0
                and self._positions
                and self._positions[0].direction == Side.BUY
            ):
                position = self._positions[0]  # Always work with oldest position first

                # Determine how much of this long position to close
                quantity_to_close = min(position.quantity, remaining_quantity)
                remaining_quantity -= quantity_to_close

                # Update or remove the position based on how much we're closing
                if quantity_to_close < position.quantity:
                    # Partial close: reduce the position size
                    position.quantity -= quantity_to_close
                else:
                    # Complete close: remove the entire position
                    self._positions.popleft()

            # If we still have remaining quantity after closing longs, open new short position
            if remaining_quantity > 0:
                self._positions.append(
                    Position(
                        entry_time=fill.ts_event,
                        direction=Side.SELL,
                        quantity=remaining_quantity,
                        entry_price=fill.fill_at,
                        adjusted_entry_price=fill.fill_point_value_adjusted_for_commission_and_fees,
                    )
                )

        # Update performance statistics
        # Track the maximum position size reached during the backtest
        current_position_size = abs(self.get_current_position())
        self._trade_stats.max_position_size = max(
            self._trade_stats.max_position_size, current_position_size
        )

    def _flush_fills_buffer(self):
        """Flush the fills buffer to the main fills DataFrame.

        This method converts the buffered fill records to a DataFrame and appends
        them to the main fills DataFrame. The buffer is cleared after flushing.
        This batching approach improves performance when processing many fills.
        """
        if self._fills_buffer:
            # Convert buffered fills to DataFrame
            buffer_df = pd.DataFrame(self._fills_buffer)

            # Append to main fills DataFrame
            if self._fills_df.empty:
                self._fills_df = buffer_df
            else:
                # Use concat for better performance than repeated appends
                self._fills_df = pd.concat(
                    [self._fills_df, buffer_df], ignore_index=True
                )

            # Clear the buffer after flushing
            self._fills_buffer = []

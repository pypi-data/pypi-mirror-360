"""
Data structures and enums for the TTS Prototyper trading system.

This module contains all the core data classes and enumerations used throughout
the trading system, including order types, market data types, and trading entities.
"""

import dataclasses
import enum
import uuid
import pandas as pd


class RecordType(enum.Enum):
    """Enumeration of supported market data record types.

    Each record type represents a different time frame for OHLCV (Open, High, Low,
    Close, Volume) market data bars.
    """
    OHLCV_1S = 32
    OHLCV_1M = 33
    OHLCV_1H = 34
    OHLCV_1D = 35

    @classmethod
    def to_string(cls, rtype: int) -> str:
        """Convert record type value to human-readable string.

        Args:
            rtype: Integer value of the record type

        Returns:
            str: Human-readable description of the record type
        """
        match rtype:
            case cls.OHLCV_1S.value:
                return "1s bars"
            case cls.OHLCV_1M.value:
                return "1m bars"
            case cls.OHLCV_1H.value:
                return "1h bars"
            case cls.OHLCV_1D.value:
                return "1d bars"
            case _:
                return f"unknown ({rtype})"


class OrderType(enum.Enum):
    """Enumeration of supported order types.

    Defines the different types of orders that can be placed in the trading system.
    """
    MARKET = "MARKET"  # Execute immediately at current market price
    LIMIT = "LIMIT"    # Execute only at specified price or better
    STOP = "STOP"      # Execute when price reaches stop level


class Side(enum.Enum):
    """Enumeration of trading directions.

    Defines whether an order or position is long (buy) or short (sell).
    """
    BUY = "BUY"    # Long position/buy order
    SELL = "SELL"  # Short position/sell order


@dataclasses.dataclass
class OrderBase:
    """Base class for all order types.

    Contains the common fields shared by all order types including identification,
    timing, direction, and quantity information.

    Attributes:
        order_id: Unique identifier for the order
        ts_event: Timestamp when the order was created
        order_direction: Whether this is a buy or sell order
        quantity: Number of contracts/shares to trade
        expiration_time: Optional expiration time for the order (None = Good Till Cancelled)
    """
    order_id: uuid.UUID
    ts_event: pd.Timestamp
    order_direction: Side
    quantity: float
    expiration_time: pd.Timestamp = dataclasses.field(default=None)


@dataclasses.dataclass
class MarketOrder(OrderBase):
    """Market order that executes immediately at current market price.

    Market orders are executed as soon as possible at the best available price.
    They provide certainty of execution but not price.

    Attributes:
        order_type: Always set to OrderType.MARKET
    """
    order_type: OrderType = dataclasses.field(default=OrderType.MARKET)


@dataclasses.dataclass
class LimitOrder(OrderBase):
    """Limit order that executes only at specified price or better.

    Limit orders provide price certainty but not execution certainty. They will
    only execute if the market reaches the specified limit price.

    Attributes:
        limit_price: Maximum price for buy orders, minimum price for sell orders
        order_type: Always set to OrderType.LIMIT
    """
    limit_price: float = 0.0
    order_type: OrderType = dataclasses.field(default=OrderType.LIMIT)


@dataclasses.dataclass
class StopOrder(OrderBase):
    """Stop order that becomes a market order when stop price is reached.

    Stop orders are used for risk management and breakout strategies. They become
    market orders when the market price reaches the stop price level.

    Attributes:
        stop_price: Price level that triggers the order execution
        order_type: Always set to OrderType.STOP
    """
    stop_price: float = 0.0
    order_type: OrderType = dataclasses.field(default=OrderType.STOP)


@dataclasses.dataclass
class Position:
    """Represents an open trading position.

    Tracks the details of an open position including entry timing, direction,
    size, and both actual and commission-adjusted entry prices.

    Attributes:
        entry_time: When the position was opened
        direction: Whether this is a long (BUY) or short (SELL) position
        quantity: Number of contracts/shares in the position
        entry_price: Actual execution price without commission adjustments
        adjusted_entry_price: Entry price adjusted for commissions and fees
    """
    entry_time: pd.Timestamp
    direction: Side
    quantity: float
    entry_price: float
    adjusted_entry_price: float


@dataclasses.dataclass
class OrderFill:
    """Represents the execution of an order.

    Contains all details about how an order was filled including pricing,
    timing, commissions, and the commission-adjusted break-even price.

    Attributes:
        fill_id: Unique identifier for this fill
        ts_event: Timestamp when the fill occurred
        associated_order_id: ID of the order that was filled
        trade_direction: Whether this was a buy or sell execution
        quantity: Number of contracts/shares filled
        fill_at: Actual execution price
        commission_and_fees: Total commissions and fees paid
        fill_point_value_adjusted_for_commission_and_fees: Break-even price including costs
    """
    fill_id: uuid.UUID
    ts_event: pd.Timestamp
    associated_order_id: uuid.UUID
    trade_direction: Side
    quantity: float
    fill_at: float
    commission_and_fees: float
    fill_point_value_adjusted_for_commission_and_fees: float


@dataclasses.dataclass
class OrderCancellation:
    """Represents the cancellation of an order.

    Tracks when and why orders were cancelled for analysis and debugging.

    Attributes:
        cancellation_id: Unique identifier for this cancellation event
        ts_event: Timestamp when the cancellation occurred
        cancelled_order_id: ID of the order that was cancelled
        order_type: Type of the cancelled order
        cancellation_reason: Reason for cancellation (manual, expired, etc.)
        original_order: Copy of the original order that was cancelled
    """
    cancellation_id: uuid.UUID
    ts_event: pd.Timestamp
    cancelled_order_id: uuid.UUID
    order_type: OrderType
    cancellation_reason: str
    original_order: OrderBase


@dataclasses.dataclass(frozen=True)
class Contract:
    """Immutable contract specifications for a trading instrument.

    Defines all the key parameters needed for accurate trading calculations
    including pricing, commissions, and fees. The class automatically calculates
    total fees in both currency and point terms.

    Attributes:
        symbol: Trading symbol/ticker for the instrument
        point_value: Dollar value of one point move in the contract
        tick_size: Minimum price increment for the contract
        broker_commission_per_contract: Commission charged by broker per contract
        exchange_fees_per_contract: Fees charged by exchange per contract
        minimum_fees: Minimum fee amount
        total_fees_per_contract_in_instrument_currency: Auto-calculated total fees
        total_fees_per_contract_in_points: Auto-calculated total fees in points
    """
    symbol: str
    point_value: float
    tick_size: float
    broker_commission_per_contract: float
    exchange_fees_per_contract: float
    minimum_fees: float
    total_fees_per_contract_in_instrument_currency: float = dataclasses.field(
        init=False
    )
    total_fees_per_contract_in_points: float = dataclasses.field(init=False)

    def __post_init__(self):
        """Calculate derived fee fields after initialization.

        Automatically computes total fees in both currency and point terms
        based on the provided broker commission and exchange fees.
        """
        # Calculate total fees in instrument currency (dollars for most US contracts)
        object.__setattr__(
            self,
            "total_fees_per_contract_in_instrument_currency",
            self.broker_commission_per_contract + self.exchange_fees_per_contract,
        )

        # Convert total fees to points for break-even calculations
        # This is used to adjust entry prices for commission costs
        object.__setattr__(
            self,
            "total_fees_per_contract_in_points",
            self.total_fees_per_contract_in_instrument_currency / self.point_value,
        )


@dataclasses.dataclass
class Trade:
    """Represents a complete trade from flat to flat position.

    A trade encompasses the entire journey from entering a position (from flat)
    to exiting back to flat. It can include multiple fills for adds/reductions.

    Attributes:
        trade_id: Unique identifier for this trade
        entry_time: Timestamp when the trade was first opened
        exit_time: Timestamp when the trade was closed (None if still open)
        direction: Overall direction of the trade (BUY for long, SELL for short)
        max_quantity: Maximum position size reached during the trade
        entry_fills: List of fills that opened/added to the position
        exit_fills: List of fills that reduced/closed the position
        realized_pnl: Total realized profit/loss for the trade
        unrealized_pnl: Current unrealized P&L (for open trades)
        total_commission: Total commission paid for all fills in this trade
        duration: How long the trade was held (None if still open)
        is_open: Whether the trade is still open
        weighted_avg_entry_price: Volume-weighted average entry price
        weighted_avg_exit_price: Volume-weighted average exit price (None if open)
    """
    trade_id: uuid.UUID
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp = None
    direction: Side = None
    max_quantity: float = 0.0
    entry_fills: list = dataclasses.field(default_factory=list)
    exit_fills: list = dataclasses.field(default_factory=list)
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    total_commission: float = 0.0
    duration: pd.Timedelta = None
    is_open: bool = True
    weighted_avg_entry_price: float = 0.0
    weighted_avg_exit_price: float = None
    max_adverse_excursion: float = 0.0  # Worst unrealized loss during trade
    max_favorable_excursion: float = 0.0  # Best unrealized profit during trade


@dataclasses.dataclass
class BacktestStatistics:
    """Container for backtest performance statistics.

    Tracks various performance metrics during backtesting. Currently tracks
    maximum position size, but can be extended with additional metrics.

    Attributes:
        max_position_size: Largest absolute position size reached during backtest
        total_trades: Total number of completed trades
        winning_trades: Number of profitable trades
        losing_trades: Number of losing trades
    """
    max_position_size: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0

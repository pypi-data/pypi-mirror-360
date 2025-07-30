"""TTS Prototyper - Trading Strategy Prototyping and Backtesting Framework.

A comprehensive framework for developing, testing, and analyzing trading strategies
with realistic order execution simulation and position management.

This package provides:
    - Abstract base class for strategy development (TTSPrototyper)
    - Order types and execution simulation (MarketOrder, LimitOrder, StopOrder)
    - Position tracking with FIFO accounting
    - Commission and fee calculations
    - Market data handling and validation

Classes:
    TTSPrototyper: Main abstract base class for strategy development
    RecordType: Enumeration of market data time frames
    OrderType: Enumeration of order types
    Side: Enumeration of trading directions (BUY/SELL)
    OrderBase: Base class for all order types
    MarketOrder: Market order implementation
    LimitOrder: Limit order implementation
    StopOrder: Stop order implementation
    OrderFill: Order execution record
    Position: Position tracking record
    Contract: Contract specifications
    BacktestStatistics: Performance statistics container
"""

from .main import (
    # Main class
    TTSPrototyper,
    # Enums
    RecordType,
    OrderType,
    Side,
    # Order classes
    OrderBase,
    MarketOrder,
    LimitOrder,
    StopOrder,
    # Other classes
    OrderFill,
    OrderCancellation,
    Trade,
    Position,
    Contract,
    BacktestStatistics,
)

__version__ = "0.2.0"

__all__ = [
    # Main class
    "TTSPrototyper",
    # Enums
    "RecordType",
    "OrderType",
    "Side",
    # Order classes
    "OrderBase",
    "MarketOrder",
    "LimitOrder",
    "StopOrder",
    # Other classes
    "OrderFill",
    "OrderCancellation",
    "Trade",
    "Position",
    "Contract",
    "BacktestStatistics",
]

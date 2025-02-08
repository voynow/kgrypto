from typing import Any, Dict, List, Set, Tuple

import polars as pl

from src.types.strategy import Action, Trade


def calculate_smas(
    prices: List[float], short_window: int, long_window: int
) -> Tuple[float, float]:
    """
    Calculate short and long simple moving averages from a list of prices

    A simple moving average (SMA) is a calculation that takes the mean of a
    given set of prices over a specific number of days in the past

    :param prices: List of prices
    :param short_window: Short window for SMA
    :param long_window: Long window for SMA
    :return: Tuple of short and long SMAs
    """
    if len(prices) < long_window:
        return 0.0, 0.0
    short_sma = sum(prices[-short_window:]) / short_window
    long_sma = sum(prices[-long_window:]) / long_window
    return short_sma, long_sma


def generate_trade_signal(short_sma: float, long_sma: float, position: int) -> Action:
    """
    Generate trading signal based on SMA values and current position

    :param short_sma: Short SMA
    :param long_sma: Long SMA
    :param position: Current position
    :return: Trading signal
    """
    if short_sma > long_sma and position == 0:
        return Action.BUY
    elif short_sma < long_sma and position == 1:
        return Action.SELL
    return Action.HOLD


def validate_params(kwargs: Dict[str, Any], valid_params: Set[str]) -> None:
    invalid_params = set(kwargs) - valid_params
    if invalid_params:
        raise ValueError(f"Invalid parameters: {invalid_params}")


def sma_crossover(data: pl.DataFrame, **kwargs) -> List[Trade]:
    """
    Run the SMA Crossover strategy on historical market data using vectorized operations.

    :param data: Polars DataFrame with market data
    :param kwargs: Strategy parameters including short_window and long_window
    :return: List of trades
    """
    validate_params(kwargs, {"short_window", "long_window"})
    short_window = kwargs.get("short_window", 5)
    long_window = kwargs.get("long_window", 10)

    df = data.with_columns(
        [
            pl.col("close").rolling_mean(window_size=short_window).alias("short_sma"),
            pl.col("close").rolling_mean(window_size=long_window).alias("long_sma"),
        ]
    )

    df = df.with_columns(
        [
            pl.when(pl.col("short_sma").is_null() | pl.col("long_sma").is_null())
            .then(0)
            .otherwise(pl.col("short_sma").gt(pl.col("long_sma")).cast(pl.Int8))
            .alias("above_sma")
        ]
    )

    df = df.with_columns([pl.col("above_sma").diff().alias("signal_change")])

    trade_rows = df.filter(
        pl.col("signal_change").is_not_null() & (pl.col("signal_change") != 0)
    )

    trades: List[Trade] = []
    for row in trade_rows.iter_rows(named=True):
        action = Action.BUY if row["signal_change"] > 0 else Action.SELL
        trades.append(Trade(time=row["timestamp"], action=action, price=row["close"]))

    # Always close position if we end with a buy
    if trades and trades[-1].action == Action.BUY:
        last_row = data.tail(1).row(0)
        trades.append(Trade(time=last_row[0], action=Action.SELL, price=last_row[1]))
    return trades


STRATEGIES = {
    "SMA_CROSSOVER": sma_crossover,
}

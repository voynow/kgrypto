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


def sma_crossover(data: pl.DataFrame, **kwargs) -> Dict[str, List[Trade]]:
    """
    Run the SMA Crossover strategy on historical market data.

    :param data: Polars DataFrame with market data
    :param kwargs: Strategy parameters including short_window and long_window
    :return:
    """
    validate_params(kwargs, {"short_window", "long_window"})
    short_window = kwargs.get("short_window", 5)
    long_window = kwargs.get("long_window", 10)

    prices: List[float] = []
    position: int = 0
    trades: List[Trade] = []

    for bar in data.to_dicts():
        price = bar["close"]
        prices.append(price)

        short_sma, long_sma = calculate_smas(prices, short_window, long_window)
        signal = generate_trade_signal(short_sma, long_sma, position)

        if signal == Action.BUY:
            trades.append(Trade(time=bar["timestamp"], action=Action.BUY, price=price))
            position = 1
        elif signal == Action.SELL:
            trades.append(Trade(time=bar["timestamp"], action=Action.SELL, price=price))
            position = 0

    if position == 1:
        trades.append(
            Trade(time=bar["timestamp"], action=Action.SELL, price=prices[-1])
        )

    return trades


STRATEGIES = {
    "SMA_CROSSOVER": sma_crossover,
}

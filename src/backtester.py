from typing import List

import polars as pl

from src.strategy import STRATEGIES
from src.types.backtester import BacktestResponse, Performance
from src.types.strategy import Action, Trade


def create_baseline_trades(data: pl.DataFrame) -> List[Trade]:
    """Baseline performance of buy and hold strategy"""
    first_timestamp = data.get_column("timestamp").min()
    last_timestamp = data.get_column("timestamp").max()
    return [
        Trade(
            time=first_timestamp,
            action=Action.BUY,
            price=data.get_column("close").min(),
        ),
        Trade(
            time=last_timestamp,
            action=Action.SELL,
            price=data.get_column("close").max(),
        ),
    ]


def validate_trades(trades: List[Trade]) -> None:
    """Validate trades"""
    if len(trades) % 2 != 0:
        raise ValueError("Trades must be a pair of buy and sell trades")
    if trades[0].action != Action.BUY:
        raise ValueError("First trade must be a buy trade")
    if trades[-1].action != Action.SELL:
        raise ValueError("Last trade must be a sell trade")


def calculate_performance(trades: List[Trade]) -> Performance:
    """Calculate performance of trades"""
    p_and_l = 0
    for i in range(0, len(trades), 2):
        buy_trade = trades[i]
        sell_trade = trades[i + 1]
        p_and_l += sell_trade.price - buy_trade.price
    return Performance(
        p_and_l_absolute=round(p_and_l, 3),
        p_and_l_percentage=round(p_and_l / trades[0].price * 100, 3),
    )


def backtest(data: pl.DataFrame, strategy: str, **kwargs) -> BacktestResponse:
    strategy_func = STRATEGIES[strategy]
    response = strategy_func(data, **kwargs)
    baseline = create_baseline_trades(data)
    return BacktestResponse(
        strategy_name=strategy,
        strategy_performance=calculate_performance(response),
        baseline_performance=calculate_performance(baseline),
        strategy_trades=response,
        baseline_trades=baseline,
    )

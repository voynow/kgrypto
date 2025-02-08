import time
from typing import List

import polars as pl

from src.strategy import STRATEGIES
from src.types.backtester import BacktestResponse, Performance
from src.types.strategy import Action, Trade


def create_baseline_trades(data: pl.DataFrame) -> List[Trade]:
    """Baseline performance of buy and hold strategy"""
    first_row = data.head(1)
    last_row = data.tail(1)
    return [
        Trade(
            time=first_row.get_column("timestamp")[0],
            action=Action.BUY,
            price=first_row.get_column("close")[0],
        ),
        Trade(
            time=last_row.get_column("timestamp")[0],
            action=Action.SELL,
            price=last_row.get_column("close")[0],
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
    validate_trades(trades)

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
        kwargs=kwargs,
    )

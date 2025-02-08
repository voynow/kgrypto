from itertools import product
from multiprocessing import Pool
from typing import Any, Dict, List

import polars as pl

from src import plotting, retriever
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


def backtest(
    data: pl.DataFrame, strategy: str, **kwargs: Dict[str, Any]
) -> BacktestResponse:
    strategy_func = STRATEGIES[strategy]
    response = strategy_func(data, **kwargs)
    baseline = create_baseline_trades(data)
    return BacktestResponse(
        strategy_name=strategy,
        strategy_performance=calculate_performance(response),
        baseline_performance=calculate_performance(baseline),
        kwargs=kwargs,
    )


def backtest_with_params(
    df: pl.DataFrame, strategy: str, params: Dict[str, Any]
) -> BacktestResponse:
    """Run backtest with given parameters."""
    return backtest(df, strategy, **params)


def parameter_search(
    ticker: str = "X:BTCUSD",
    from_date: str = "2024-01-01",
    to_date: str = "2025-01-01",
    strategy: str = "SMA_CROSSOVER",
    short_window_start: int = 10,
    short_window_end: int = 290,
    long_window_end: int = 300,
    step: int = 5,
    n_processes: int = 5,
) -> List[BacktestResponse]:
    """Search through parameter combinations for a given strategy in parallel."""
    # Retrieve and plot the data
    df = retriever.agg_cache_wrapper(
        ticker=ticker, from_date=from_date, to_date=to_date
    )
    plotting.plot_agg_df(df, ticker=ticker)

    # Generate parameter combinations ensuring short_window < long_window
    param_combinations = [
        {"short_window": sw, "long_window": lw}
        for sw in range(short_window_start, short_window_end, step)
        for lw in range(sw + step, long_window_end, step)
    ]

    # Run backtests in parallel
    with Pool(n_processes) as pool:
        results = pool.starmap(
            backtest_with_params,
            [(df, strategy, param) for param in param_combinations],
        )

    # Plot and return results
    plotting.plot_strategy_performance(results)
    return results

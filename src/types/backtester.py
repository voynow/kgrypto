from typing import List

from pydantic import BaseModel

from src.types.strategy import Trade


class Performance(BaseModel):
    p_and_l_absolute: float
    p_and_l_percentage: float


class BacktestResponse(BaseModel):
    strategy_name: str
    strategy_performance: Performance
    baseline_performance: Performance
    strategy_trades: List[Trade]
    baseline_trades: List[Trade]

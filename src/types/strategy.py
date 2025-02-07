from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class Action(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class Trade(BaseModel):
    time: datetime
    action: Action
    price: float

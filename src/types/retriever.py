from datetime import datetime

from typing import Optional

from pydantic import BaseModel, Field


class Agg(BaseModel):
    """
    Custom agg data model (inspired by polygon.rest.models.aggs.Agg) where
    timestamp is represented as datetime

    :open: float - Open price at the start of the time window
    :high: float - Highest price during the time window
    :low: float - Lowest price during the time window
    :close: float - Close price at the end of the time window
    :volume: float - Volume of shares traded during the time window
    :vwap: float - Volume-weighted average price during the time window
    :timestamp: datetime - Timestamp of the start of the time window
    :transactions: int - Number of transactions during the time window
    :otc: bool - Whether the stock is traded on the OTC market
    """

    open: Optional[float] = Field(None, alias="o")
    high: Optional[float] = Field(None, alias="h")
    low: Optional[float] = Field(None, alias="l")
    close: Optional[float] = Field(None, alias="c")
    volume: Optional[float] = Field(None, alias="v")
    vwap: Optional[float] = Field(None, alias="vw")
    timestamp: Optional[datetime] = Field(
        None, alias="t", pre=lambda x: datetime.fromtimestamp(x / 1000) if x else None
    )
    transactions: Optional[int] = Field(None, alias="n")
    otc: Optional[bool] = None

    class Config:
        # Convert from alias to field name on deserialization
        populate_by_name = True

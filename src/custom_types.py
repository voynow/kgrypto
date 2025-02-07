from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Agg(BaseModel):
    """
    Custom agg data model (inspired by polygon.rest.models.aggs.Agg) where
    timestamp is represented as datetime
    """

    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[float] = None
    vwap: Optional[float] = None
    timestamp: Optional[datetime] = None
    transactions: Optional[int] = None
    otc: Optional[bool] = None

    @staticmethod
    def from_dict(d):
        """
        Convert a dictionary to an Agg object, transforming the timestamp to a datetime object

        :param d: dictionary to convert to Agg object
        :return: Agg object
        """
        timestamp = d.get("t")
        dt = datetime.fromtimestamp(timestamp / 1000) if timestamp else None

        return Agg(
            open=d.get("o", None),
            high=d.get("h", None),
            low=d.get("l", None),
            close=d.get("c", None),
            volume=d.get("v", None),
            vwap=d.get("vw", None),
            timestamp=dt,
            transactions=d.get("n", None),
            otc=d.get("otc", None),
        )

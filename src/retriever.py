import os
from datetime import datetime
from typing import List

import polars as pl
from polygon import RESTClient

from src.constants import DATA_DIR
from src.types.retriever import Agg

client = RESTClient(api_key=os.environ["POLYGON_API_KEY"])


def agg(ticker: str, from_date: str, to_date: str) -> List[Agg]:

    aggs = []
    for item in client.list_aggs(
        ticker=ticker,
        multiplier=1,
        timespan="minute",
        from_=from_date,
        to=to_date,
    ):
        raw_item = item.__dict__
        raw_item["timestamp"] = datetime.fromtimestamp(raw_item["timestamp"] / 1000)
        aggs.append(Agg(**raw_item))

    return aggs


def agg_to_df(ticker: str, start_date: str, end_date: str) -> pl.DataFrame:
    """
    :param ticker: Ticker symbol to pull data for.
    :param start_date: Start date (YYYY-MM-DD).
    :param end_date: End date (YYYY-MM-DD).
    :return: Polars DataFrame of Agg data fetched from Polygon.
    """

    results = agg(ticker, start_date, end_date)
    return pl.DataFrame([r.model_dump() for r in results])


def agg_cache_wrapper(ticker: str, from_date: str, to_date: str) -> pl.DataFrame:
    """
    :param ticker: Ticker symbol to load.
    :param from_date: Start date (YYYY-MM-DD) to ensure coverage.
    :param to_date: End date (YYYY-MM-DD) to ensure coverage.
    :return: Polars DataFrame containing at least [from_date, to_date] range.
    """
    parquet_path = os.path.join(DATA_DIR, f"{ticker}.parquet")
    from_dt = datetime.strptime(from_date, "%Y-%m-%d")
    to_dt = datetime.strptime(to_date, "%Y-%m-%d")

    # cache miss
    if not os.path.exists(parquet_path):
        df_new = agg_to_df(ticker, from_date, to_date)
        df_new.write_parquet(parquet_path)
        return df_new

    # potential cache hit
    df_existing = pl.read_parquet(parquet_path)
    min_ts = df_existing["timestamp"].min()
    max_ts = df_existing["timestamp"].max()

    # pull missing older data if needed
    df_to_append = []
    if from_dt < min_ts:
        df_old = agg_to_df(ticker, from_date, min_ts.strftime("%Y-%m-%d"))
        df_to_append.append(df_old)
    if to_dt > max_ts:
        df_new = agg_to_df(ticker, max_ts.strftime("%Y-%m-%d"), to_date)
        df_to_append.append(df_new)

    # Merge old+new into existing
    if df_to_append:
        df_to_append = pl.concat(df_to_append, how="vertical")
        df_combined = pl.concat([df_existing, df_to_append], how="vertical")
        df_combined = df_combined.unique(subset=["timestamp"], keep="last").sort(
            "timestamp"
        )
        df_combined.write_parquet(parquet_path)
    else:
        df_combined = df_existing

    mask = (pl.col("timestamp") >= from_dt) & (pl.col("timestamp") <= to_dt)
    return df_combined.filter(mask)

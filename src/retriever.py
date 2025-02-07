import os

from polygon import RESTClient

from src.custom_types import Agg

client = RESTClient(api_key=os.environ["POLYGON_API_KEY"])


def get_agg_data(ticker: str, from_date: str, to_date: str) -> list[Agg]:
    """
    Get data from ticker conforming to Agg data model

    :param ticker: asset ticker (e.g. "SOL")
    :param from_date: start date (e.g. "2024-04-01")
    :param to_date: end date (e.g. "2024-04-04")
    """
    response = client.get_aggs(
        ticker=ticker,
        multiplier=1,
        timespan="hour",
        from_=from_date,
        to=to_date,
        raw=True,
    )

    agg_data = response.json()
    if agg_data["status"] != "OK":
        raise Exception(f"API request failed with status: {agg_data['status']}")

    return [Agg.from_dict(result) for result in agg_data["results"]]

import plotly.graph_objects as go
import polars as pl


def plot_agg_df(df: pl.DataFrame, ticker: str, y: list[str] = ["open"]):
    """
    Plots financial data using Plotly (line chart only). The DataFrame must have a 'timestamp'
    column of datetime objects. The chart title is derived from the first and last timestamp.

    :param df: Polars DataFrame with a 'timestamp' column.
    :param ticker: Financial instrument ticker (e.g., "X:BTCUSD").
    :param y: List of y-axis column names.
    """
    df = df.sort("timestamp")
    start_date = df["timestamp"][0].strftime("%Y-%m-%d")
    end_date = df["timestamp"][-1].strftime("%Y-%m-%d")
    title = f"{ticker} Prices {start_date} → {end_date}"

    fig = go.Figure()
    for col in y:
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"].to_list(),
                y=df[col].to_list(),
                mode="lines",
                name=f"{ticker} {col}",
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="timestamp",
        yaxis_title="Price",
        template="plotly_dark",
    )
    fig.show()

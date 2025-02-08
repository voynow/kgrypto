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


def plot_strategy_performance(results: list):
    """
    Plots a 3D scatter plot showing strategy performance in relation to short_window and long_window.

    :param results: List of strategy results, where each result has
                    - `strategy_performance.p_and_l_percentage`
                    - `kwargs['short_window']`
                    - `kwargs['long_window']`
    """
    print(
        f"Baseline performance to beat: {results[0].baseline_performance.p_and_l_percentage}%"
    )
    short_windows = [res.kwargs["short_window"] for res in results]
    long_windows = [res.kwargs["long_window"] for res in results]
    pnl_values = [res.strategy_performance.p_and_l_percentage for res in results]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter3d(
            x=short_windows,
            y=long_windows,
            z=pnl_values,
            mode="markers",
            marker=dict(
                size=6,
                color=pnl_values,
                colorscale="Viridis",
                colorbar=dict(title="P&L %"),
                opacity=0.8,
            ),
        )
    )

    fig.update_layout(
        title="Strategy Performance vs Short & Long Window",
        scene=dict(
            xaxis_title="Short Window",
            yaxis_title="Long Window",
            zaxis_title="P&L Percentage",
        ),
        template="plotly_dark",
    )

    fig.show()

from retriever import load_or_update_agg_data
from backtester import backtest
from strategy import SMACrossover

DATA_DIR = "local_cache"
TICKER = "BTCUSD"
START_DATE = "2023-01-01"
END_DATE = "2023-01-15"

df = load_or_update_agg_data(TICKER, START_DATE, END_DATE, DATA_DIR)

strategy = SMACrossover(short_window=5, long_window=10)
backtest(df, strategy)

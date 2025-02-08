# kgrypto

A super chill crypto backtesting system

## Setup

1. Clone the repo

    ```
    git clone https://github.com/voynow/kgrypto.git
    ```

2. Install dependencies with PDM:

    ```
    pdm install
    ```

3. Activate your virtual environment:

   ```
   source .venv/bin/activate
   ```

## How It Works

- **Data Retrieval & Caching:**  
  src/retriever.py pulls data from Polygon and caches it as Parquet files in local_cache/

- **Backtesting Engine:**  
  src/backtester.py runs the backtest on cached data
  Strategies live in src/strategy.py and are executed via the STRATEGIES registry

- **Entry Point:**  
  Use src/main.py to kick off a backtest with default parameters

- **Plotting & Analysis:**  
  src/plotting.py and src/analysis.py handle visualization and performance metrics

## Relevant files

- backtester.py   – Core backtesting engine
- retriever.py    – Data pulling and caching logic
- strategy.py     – Trading strategies (e.g. SMA crossover)
- plotting.py     – Plotting functions
- constants.py    – Shared constants
- custom_types.py – Shared types and models


